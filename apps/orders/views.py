from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.utils import timezone
from django.db.models import F, Sum, Q
from datetime import timedelta
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from decimal import Decimal
import json

from apps.authentication.decorators import role_required
from apps.menu.models import Plat
from apps.tables.models import TableRestaurant
from .models import Panier, PanierItem, Commande, CommandeItem
from .forms import AddToCartForm, UpdateCartItemForm, CreateOrderForm

from django.views.decorators.cache import cache_page
from django.core.cache import cache

@role_required(['Rtable', 'Radmin'])
# @cache_page(30)  # Cache désactivé pour le debug
def view_cart(request):
    # Cache désactivé pour le debug
    # cache_key = f'cart_{request.user.id}'
    # cached_data = cache.get(cache_key)
    
    # if cached_data is None:
    # Récupérer le panier actif de la table de l'utilisateur avec des requêtes optimisées
    table = request.user.tables.first()
    
    if not table:
        messages.error(request, "Aucune table n'est associée à votre compte.")
        return redirect('menu:list_dishes')
        
    try:
        # Utilisation de select_related et prefetch_related pour optimiser les requêtes
        panier = Panier.objects.select_related('table').prefetch_related(
            'items__plat'
        ).get(table=table, is_active=True)
        
        items = list(
            panier.items.select_related('plat').only(
                'id', 'quantite', 'prix_unitaire', 'notes',
                'plat__id', 'plat__nom', 'plat__prix_unitaire'
            ).all()
        )
        
        # Calculer le total manuellement pour éviter des requêtes supplémentaires
        total = sum(item.prix_unitaire * item.quantite for item in items)
        
    except Panier.DoesNotExist:
        panier = None
        items = []
        total = Decimal('0.00')
    
    # Préparer le contexte
    context = {
        'panier': panier,
        'items': items,
        'total': total,
    }
    
    # Mettre en cache pendant 30 secondes
    # cache.set(cache_key, context, 30)
    # else:
    #     context = cached_data
    
    return render(request, 'orders/view_cart.html', context)

@csrf_exempt
@login_required
@role_required(['Rtable', 'Rservent', 'Radmin'])
def add_to_cart(request, plat_id):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Méthode non autorisée'
        }, status=405)
    
    try:
        # Récupérer les données du formulaire
        quantite = int(request.POST.get('quantite', 1))
        notes = request.POST.get('notes', '')
        
        # Récupérer la table de l'utilisateur connecté via QR
        table = request.user.tables.first()
        
        if not table:
            messages.error(request, "Aucune table trouvée pour votre compte.")
            return redirect('menu:list_dishes')
            
        plat = get_object_or_404(Plat, id=plat_id, disponible=True)
        
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
            
            messages.success(request, f"{plat.nom} a été ajouté à votre panier.")
            
            # Retourner une réponse JSON pour AJAX
            return JsonResponse({
                'success': True,
                'message': f"{plat.nom} a été ajouté à votre panier.",
                'cart_count': panier.items.count(),
                'cart_total': str(panier.total)
            })
            
    except (Plat.DoesNotExist, TableRestaurant.DoesNotExist, ValueError) as e:
        return JsonResponse({
            'success': False,
            'message': str(e) if str(e) else 'Erreur lors de l\'ajout au panier'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Une erreur est survenue lors de l\'ajout au panier.'
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
        
    try:
        item = PanierItem.objects.get(id=item_id, panier__table=table)
    except PanierItem.DoesNotExist:
        messages.error(request, "Cet article n'existe plus dans votre panier.")
        return redirect('orders:view_cart')
    
    if request.method == 'POST':
        form = UpdateCartItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Quantité mise à jour avec succès.")
            
            if request.headers.get('HX-Request'):
                from django.template.loader import render_to_string
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
def remove_from_cart_view(request, item_id):
    table = request.user.tables.first()
    if not table:
        messages.error(request, "Aucune table n'est associée à votre compte.")
        return redirect('menu:list_dishes')
    
    try:
        item = PanierItem.objects.get(id=item_id, panier__table=table)
    except PanierItem.DoesNotExist:
        messages.error(request, "Cet article n'existe plus dans votre panier.")
        return redirect('orders:view_cart')
    
    if request.method == 'POST':
        panier = item.panier
        item.delete()
        messages.success(request, "Article retiré du panier.")
        
        if request.headers.get('HX-Request'):
            from django.template.loader import render_to_string
            items = panier.items.select_related('plat').all()
            html = render_to_string('orders/partials/cart_items.html', {
                'items': items,
                'total': panier.total if items else Decimal('0.00')
            })
            return HttpResponse(html)
        
        return redirect('orders:view_cart')
    
    return render(request, 'orders/remove_from_cart.html', {'item': item})

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

@role_required(['Rtable', 'Rservent', 'Radmin', 'Rcaissier'])
@transaction.atomic
@login_required
def list_orders(request):
    # IMPORTANT: ne pas mettre en cache cette page car elle affiche des messages
    # (sinon on risque d'afficher des messages obsolètes après navigation).
    statut = request.GET.get('statut')

    # Si l'utilisateur est une table, ne montrer que ses commandes
    if request.user.role == 'Rtable':
        table = request.user.tables.first()
        if not table:
            messages.error(request, "Aucune table n'est associée à votre compte.")
            return redirect('menu:list_dishes')
        
        base_qs = Commande.objects.filter(table=table)
    else:
        base_qs = Commande.objects.all()

    if statut in ['en_attente', 'servie', 'payee']:
        orders = base_qs.filter(statut=statut)
    else:
        orders = base_qs.filter(statut__in=['en_attente', 'servie'])

    orders = orders.select_related('table').prefetch_related(
        'items__plat'
    ).order_by('-date_commande').only(
        'id', 'date_commande', 'statut', 'montant_total', 'numero_commande',
        'table__numero_table'
    )

    total_commande = orders.aggregate(total=Sum('montant_total'))['total'] or 0
    commandes_en_attente = base_qs.filter(statut='en_attente').count()
    commandes_servies = base_qs.filter(statut='servie').count()

    context = {
        'commandes': orders,
        'total_commande': total_commande,
        'commandes_en_attente': commandes_en_attente,
        'commandes_servies': commandes_servies,
        'tables': TableRestaurant.objects.all().order_by('numero_table'),
    }

    return render(request, 'orders/list_orders.html', context)


@role_required(['Rservent', 'Radmin', 'Rcaissier'])
@transaction.atomic
def start_table_order(request):
    if request.method != 'POST':
        return redirect('orders:list_orders')

    table_id = request.POST.get('table_id')
    if not table_id:
        messages.error(request, "Veuillez sélectionner une table.")
        return redirect('orders:list_orders')

    table = get_object_or_404(TableRestaurant, id=table_id)

    # Démarrer une nouvelle commande = nouveau panier actif
    Panier.objects.filter(table=table, is_active=True).update(is_active=False)
    Panier.objects.create(
        table=table,
        created_by=request.user,
        is_active=True
    )

    messages.success(request, f"Nouvelle commande démarrée pour la table {table.numero_table}.")
    return redirect('tables:table_detail', table_id=table.id)

@role_required(['Rservent', 'Radmin', 'Rcaissier'])
def view_order(request, order_id):
    commande = get_object_or_404(Commande, id=order_id)
    items = commande.items.select_related('plat').all()
    
    return render(request, 'orders/view_order.html', {
        'commande': commande,
        'items': items
    })


@role_required(['Rcaissier', 'Radmin'])
def invoice_order(request, order_id):
    """Génère une facture pour une commande"""
    commande = get_object_or_404(Commande, id=order_id)
    items = commande.items.select_related('plat').all()
    
    return render(request, 'orders/invoice.html', {
        'commande': commande,
        'items': items
    })

@role_required(['Rservent', 'Radmin', 'Rcaissier'])
def mark_order_served(request, order_id):
    commande = get_object_or_404(Commande, id=order_id)

    if commande.statut != 'en_attente':
        messages.warning(
            request,
            f"La commande {commande.numero_commande} n'est plus en attente (statut: {commande.get_statut_display()})."
        )
        return redirect('orders:list_orders')

    if request.method == 'POST':
        commande.statut = 'servie'
        commande.date_service = timezone.now()
        commande.validateur = request.user
        commande.save()

        messages.success(request, f"La commande {commande.numero_commande} a été marquée comme servie.")
        return redirect('orders:list_orders')

    return render(request, 'orders/mark_order_served.html', {'commande': commande})

@role_required(['Rservent', 'Radmin', 'Rcaissier'])
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
                # Sécuriser le statut de la commande (au cas où la logique du modèle change)
                commande.statut = 'payee'
                commande.caissier = request.user
                commande.save()
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

@role_required(['Rservent', 'Radmin', 'Rcaissier'])
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
        montant = commande.montant_total
        
        # Créer le paiement (le modèle Paiement est en OneToOne: un seul paiement par commande)
        with transaction.atomic():
            paiement = Paiement.objects.create(
                commande=commande,
                caisse=caisse,
                montant=montant,
                mode_paiement=mode_paiement,
                utilisateur=request.user,
                est_valide=False,
            )
        
        return redirect('orders:confirm_payment', payment_id=paiement.id)
     
    return render(request, 'orders/mark_order_paid.html', {
        'commande': commande,
        'caisse': caisse
    })

@role_required(['Rtable', 'Radmin'])
def order_history(request):
    # Récupérer la table de l'utilisateur
    table = request.user.tables.first()
    if not table:
        messages.error(request, "Aucune table n'est associée à votre compte.")
        return redirect('menu:list_dishes')
    
    # Récupérer l'historique des commandes pour cette table
    commandes = Commande.objects.filter(table=table).order_by('-date_commande')
    
    return render(request, 'orders/order_history.html', {
        'commandes': commandes
    })


@role_required(['Radmin', 'Rcaissier'])
def sales_history(request):
    """Vue pour l'historique des ventes avec filtres par période"""
    today = timezone.now().date()
    
    # Gérer les filtres de période
    period = request.GET.get('period', 'today')
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    # Base queryset - toutes les commandes payées
    queryset = Commande.objects.filter(statut='payee').select_related(
        'table', 'serveur', 'validateur', 'caissier'
    ).order_by('-date_paiement')
    
    # Appliquer les filtres de période
    if period == 'today':
        queryset = queryset.filter(date_paiement__date=today)
    elif period == 'yesterday':
        yesterday = today - timedelta(days=1)
        queryset = queryset.filter(date_paiement__date=yesterday)
    elif period == 'before_yesterday':
        before_yesterday = today - timedelta(days=2)
        queryset = queryset.filter(date_paiement__date=before_yesterday)
    elif period == 'week':
        week_ago = today - timedelta(days=7)
        queryset = queryset.filter(date_paiement__date__gte=week_ago)
    elif period == 'month':
        month_ago = today - timedelta(days=30)
        queryset = queryset.filter(date_paiement__date__gte=month_ago)
    elif period == 'last_month':
        from datetime import datetime
        first_day_this_month = today.replace(day=1)
        last_day_last_month = first_day_this_month - timedelta(days=1)
        first_day_last_month = last_day_last_month.replace(day=1)
        queryset = queryset.filter(
            date_paiement__date__gte=first_day_last_month,
            date_paiement__date__lte=last_day_last_month
        )
    elif period == 'year':
        year_ago = today - timedelta(days=365)
        queryset = queryset.filter(date_paiement__date__gte=year_ago)
    elif period == 'custom' and date_debut and date_fin:
        queryset = queryset.filter(
            date_paiement__date__gte=date_debut,
            date_paiement__date__lte=date_fin
        )
    
    # Calculer les statistiques
    total_ventes = queryset.aggregate(total=Sum('montant_total'))['total'] or Decimal('0.00')
    nombre_commandes = queryset.count()
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(queryset, 50)
    page = request.GET.get('page', 1)
    try:
        commandes = paginator.page(page)
    except:
        commandes = paginator.page(1)
    
    context = {
        'commandes': commandes,
        'total_ventes': total_ventes,
        'nombre_commandes': nombre_commandes,
        'period': period,
        'date_debut': date_debut,
        'date_fin': date_fin,
    }
    
    return render(request, 'orders/sales_history.html', context)


@role_required(['Rcaissier', 'Radmin'])
def invoice_order(request, order_id):
    """Génère une facture pour une commande"""
    commande = get_object_or_404(Commande, id=order_id)
    items = commande.items.select_related('plat').all()
    
    return render(request, 'orders/invoice.html', {
        'commande': commande,
        'items': items
    })
@role_required(['Rtable', 'Radmin'])
def delete_order(request, order_id):
    """Supprimer une commande (uniquement si elle est en attente)"""
    commande = get_object_or_404(Commande, id=order_id)
    
    # Vérifier les permissions
    if request.user.role == 'Rtable':
        # Les utilisateurs de table ne peuvent supprimer que leurs propres commandes
        table = request.user.tables.first()
        if not table or commande.table != table:
            messages.error(request, "Vous n'avez pas la permission de supprimer cette commande.")
            return redirect('orders:list_orders')
    
    # Vérifier que la commande est en attente (seul ce statut peut être supprimé)
    if commande.statut != 'en_attente':
        messages.error(request, f"Impossible de supprimer la commande {commande.numero_commande} car elle est déjà {commande.get_statut_display()}.")
        return redirect('orders:list_orders')
    
    if request.method == 'POST':
        # Confirmer la suppression
        commande_numero = commande.numero_commande
        commande.delete()
        messages.success(request, f"La commande {commande_numero} a été supprimée avec succès.")
        return redirect('orders:list_orders')
    
    # Afficher la page de confirmation
    return render(request, 'orders/delete_order.html', {'commande': commande})
