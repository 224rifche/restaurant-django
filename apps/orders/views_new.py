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
        
        plat = get_object_or_404(Plat, id=plat_id, est_actif=True)
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
                    'prix_unitaire': plat.prix,
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

# Autres vues existantes...
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
                    statut='en_attente',
                    serveur=request.user
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
                
                # Désactiver le panier actuel
                panier.is_active = False
                panier.save()
                
                messages.success(request, 'Commande passée avec succès!')
                return redirect('tables:table_detail', table_id=table.id)
    else:
        form = CreateOrderForm()
    
    return render(request, 'orders/create_order.html', {
        'form': form,
        'panier': panier,
        'items': items,
        'total': panier.total
    })
