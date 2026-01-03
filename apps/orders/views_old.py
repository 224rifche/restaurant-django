from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.db.models import F, Sum, Q
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from decimal import Decimal
import json

from apps.authentication.decorators import role_required
from apps.menu.models import Plat
from apps.tables.models import TableRestaurant
from .models import Panier, PanierItem, Commande, CommandeItem
from .forms import AddToCartForm, UpdateCartItemForm, CreateOrderForm


@role_required(['Rtable', 'Radmin'])
def view_cart(request):
    # Récupérer le panier actif de la table de l'utilisateur
    table = request.user.tables.first()
    if not table:
        messages.error(request, "Aucune table n'est associée à votre compte.")
        return redirect('menu:list_dishes')
        
    try:
        panier = Panier.objects.get(table=table, is_active=True)
    except Panier.DoesNotExist:
        panier = None
    
    context = {
        'panier': panier,
        'items': panier.items.select_related('plat').all() if panier else [],
        'total': panier.total if panier else Decimal('0.00'),
    }
    return render(request, 'orders/view_cart.html', context)


@require_POST
@csrf_exempt
@role_required(['Rservent', 'Radmin'])
def add_to_cart(request):
    try:
        data = json.loads(request.body)
        plat_id = data.get('plat_id')
        quantite = int(data.get('quantite', 1))
        notes = data.get('notes', '')
        table_id = data.get('table_id')
        
        if not plat_id or not table_id:
            return JsonResponse({
                'success': False,
                'message': 'Données manquantes'
            }, status=400)
        
        plat = get_object_or_404(Plat, id=plat_id, disponible=True)
        table = get_object_or_404(TableRestaurant, id=table_id)
        
        with transaction.atomic():
            # Récupérer ou créer un panier actif pour la table
            panier, created = Panier.objects.get_or_create(
                table=table,
                is_active=True,
                defaults={'created_by': request.user}
            )
            
            # Vérifier si l'article est déjà dans le panier
            panier_item, created = PanierItem.objects.get_or_create(
                panier=panier,
                plat=plat,
                defaults={
                    'prix_unitaire': plat.prix_unitaire,
                    'quantite': quantite,
                    'notes': notes
                }
            )
            
            if not created:
                # Mettre à jour la quantité si l'article existe déjà
                panier_item.quantite += quantite
                panier_item.notes = notes or panier_item.notes
                panier_item.save()
            
            return JsonResponse({
                'success': True,
                'panier_total': str(panier.total),
                'item_count': panier.items.count()
            })
            
    except (Plat.DoesNotExist, TableRestaurant.DoesNotExist, ValueError) as e:
        return JsonResponse({
            'success': False,
            'message': str(e) if str(e) else 'Erreur lors de l\'ajout au panier'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Une erreur est survenue',
            'error': str(e)
        }, status=500)


@require_POST
@csrf_exempt
@role_required(['Rservent', 'Radmin'])
def remove_from_cart(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        
        if not item_id:
            return JsonResponse({
                'success': False,
                'message': 'ID de l\'article manquant'
            }, status=400)
        
        # Vérifier que l'utilisateur a le droit de modifier ce panier
        panier_item = PanierItem.objects.select_related('panier').get(
            id=item_id,
            panier__is_active=True
        )
        
        panier = panier_item.panier
        panier_item.delete()
        
        return JsonResponse({
            'success': True,
            'panier_total': str(panier.total),
            'item_count': panier.items.count()
        })
        
    except PanierItem.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Article non trouvé ou déjà supprimé'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Erreur lors de la suppression',
            'error': str(e)
        }, status=500)


@role_required(['Rtable', 'Radmin'])
def update_cart_item(request, item_id):
    table = request.user.tables.first()
    if not table:
        messages.error(request, "Aucune table n'est associée à votre compte.")
        return redirect('menu:list_dishes')
        
    item = get_object_or_404(PanierItem, id=item_id, panier__table=table)
    
    if request.method == 'POST':
        form = UpdateCartItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Quantité mise à jour avec succès.")
            
            if request.headers.get('HX-Request'):
                from django.template.loader import render_to_string
                from django.http import HttpResponse
                
                panier = item.panier
                items = panier.items.select_related('plat').all()
                html = render_to_string('orders/partials/cart_items.html', {
                    'items': items,
                    'total': panier.total
                })
                return HttpResponse(html)
            
            return redirect('orders:view_cart')
    else:
        form = UpdateCartItemForm(instance=item)
    
    return render(request, 'orders/update_cart_item.html', {
        'form': form,
        'item': item
    })


@role_required(['Rtable', 'Radmin'])
def create_order(request):
    # Récupérer la table de l'utilisateur
    table = request.user.tables.first()
    if not table:
        messages.error(request, "Aucune table n'est associée à votre compte.")
        return redirect('menu:list_dishes')
    
    try:
        panier = Panier.objects.get(table=table, is_active=True)
    except Panier.DoesNotExist:
        messages.error(request, "Votre panier est vide.")
        return redirect('menu:list_dishes')
    
    items = panier.items.select_related('plat').all()
    
    if not items:
        messages.error(request, "Votre panier est vide.")
        return redirect('menu:list_dishes')
    
    if request.method == 'POST':
        form = CreateOrderForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Créer la commande
                commande = Commande.objects.create(
                    table=table,
                    montant_total=panier.total,
                    notes=form.cleaned_data['notes'],
                    statut='en_attente'
                )
                
                # Créer les éléments de la commande
                for item in items:
                    CommandeItem.objects.create(
                        commande=commande,
                        plat=item.plat,
                        quantite=item.quantite,
                        prix_unitaire=item.prix_unitaire,
                        notes=item.notes
                    )
                
                # Désactiver le panier
                panier.is_active = False
                panier.save()
                
                # Créer un nouveau panier vide pour la table
                Panier.objects.create(table=table, is_active=True)
                
                messages.success(request, "Votre commande a été passée avec succès !")
                return redirect('orders:order_confirmation', order_id=commande.id)
    else:
        form = CreateOrderForm()
    
    return render(request, 'orders/create_order.html', {
        'form': form,
        'panier': panier,
        'items': items,
        'total': panier.total
    })


@role_required(['Rtable', 'Radmin'])
def order_confirmation(request, order_id):
    # Récupérer la table de l'utilisateur
    table = request.user.tables.first()
    if not table:
        messages.error(request, "Aucune table n'est associée à votre compte.")
        return redirect('menu:list_dishes')
    
    # Récupérer la commande pour cette table
    commande = get_object_or_404(Commande, id=order_id, table=table)
    return render(request, 'orders/order_confirmation.html', {'commande': commande})


@role_required(['Rservent', 'Radmin'])
def list_orders(request):
    statut = request.GET.get('statut', 'en_attente')
    
    if statut == 'tous':
        commandes = Commande.objects.all()
    else:
        commandes = Commande.objects.filter(statut=statut)
    
    commandes = commandes.select_related('table').order_by('-date_commande')
    
    return render(request, 'orders/list_orders.html', {
        'commandes': commandes,
        'statut': statut,
        'statuts': dict(Commande.STATUT_CHOICES)
    })


@role_required(['Rservent', 'Radmin'])
def view_order(request, order_id):
    commande = get_object_or_404(Commande, id=order_id)
    items = commande.items.select_related('plat').all()
    
    return render(request, 'orders/view_order.html', {
        'commande': commande,
        'items': items
    })


@role_required(['Rservent', 'Radmin'])
def mark_order_served(request, order_id):
    commande = get_object_or_404(Commande, id=order_id, statut='en_attente')
    
    if request.method == 'POST':
        commande.statut = 'servie'
        commande.save()
        
        messages.success(request, f"La commande {commande.numero_commande} a été marquée comme servie.")
        return redirect('orders:list_orders')
    
    return render(request, 'orders/mark_order_served.html', {'commande': commande})


@role_required(['Rservent', 'Radmin'])
def confirm_payment(request, payment_id):
    from apps.payments.models import Paiement
    
    # Récupérer le paiement
    paiement = get_object_or_404(Paiement, id=payment_id, est_valide=False)
    commande = paiement.commande
    
    if request.method == 'POST':
        if 'confirm' in request.POST:
            # Valider le paiement
            with transaction.atomic():
                # Mettre à jour le statut du paiement
                paiement.est_valide = True
                paiement.save()
                
                # Mettre à jour le statut de la commande
                commande.statut = 'payee'
                commande.save()
                
                # Mettre à jour le solde de la caisse
                paiement.caisse.solde_actuel += paiement.montant
                paiement.caisse.save()
                
                # Créer un nouveau panier vide pour la table
                Panier.objects.create(table=commande.table, is_active=True)
                
                messages.success(request, f"Paiement de {paiement.montant} GNF confirmé avec succès pour la commande {commande.numero_commande}.")
                return redirect('orders:list_orders')
        
        elif 'cancel' in request.POST:
            # Annuler le paiement
            paiement.delete()
            messages.warning(request, "Le paiement a été annulé.")
            return redirect('orders:mark_order_paid', order_id=commande.id)
    
    return render(request, 'orders/confirm_payment.html', {
        'commande': commande,
        'paiement': paiement
    })

@role_required(['Rservent', 'Radmin'])
def mark_order_paid(request, order_id):
    from apps.payments.models import Caisse, Paiement
    
    commande = get_object_or_404(Commande, id=order_id, statut='servie')
    
    # Vérifier si un paiement existe déjà pour cette commande
    if hasattr(commande, 'paiement'):
        messages.warning(request, f"Un paiement a déjà été enregistré pour la commande {commande.numero_commande}.")
        return redirect('orders:list_orders')
    
    # Vérifier qu'une caisse est ouverte
    caisse = Caisse.get_caisse_ouverte()
    if not caisse:
        messages.error(request, "Aucune caisse n'est ouverte. Veuillez ouvrir une caisse avant d'enregistrer un paiement.")
        return redirect('orders:list_orders')
    
    if request.method == 'POST':
        mode_paiement = request.POST.get('mode_paiement', 'especes')
        
        try:
            with transaction.atomic():
                # Créer d'abord l'enregistrement de paiement
                paiement = Paiement.objects.create(
                    commande=commande,
                    montant=commande.montant_total,
                    mode_paiement=mode_paiement,
                    caisse=caisse,
                    utilisateur=request.user,
                    est_valide=False  # Paiement non validé par défaut
                )
                
                # Rediriger vers la page de confirmation
                return redirect('orders:confirm_payment', payment_id=paiement.id)
                
        except Exception as e:
            messages.error(request, f"Erreur lors de la préparation du paiement : {str(e)}")
            return redirect('orders:mark_order_paid', order_id=order_id)
    
    # Afficher le formulaire de paiement
    return render(request, 'orders/mark_order_paid.html', {
        'commande': commande, 
        'caisse': caisse
    })


@role_required(['Rtable', 'Radmin'])
def order_history(request):
    # Vérifier si l'utilisateur a une table associée
    if not hasattr(request.user, 'table') or not request.user.table:
        messages.warning(request, "Aucune table n'est associée à votre compte.")
        return redirect('menu:list_dishes')
    
    # Récupérer les commandes de la table de l'utilisateur
    commandes = Commande.objects.filter(table=request.user.table).order_by('-date_commande')
    return render(request, 'orders/order_history.html', {'commandes': commandes})
