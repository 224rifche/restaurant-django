from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.db.models import F, Sum
from decimal import Decimal

from apps.authentication.decorators import role_required
from apps.menu.models import Plat
from apps.tables.models import TableRestaurant
from .models import Panier, PanierItem, Commande, CommandeItem
from .forms import AddToCartForm, UpdateCartItemForm, CreateOrderForm


@role_required(['Rtable', 'Radmin'])
def view_cart(request):
    # Récupérer le panier actif de la table de l'utilisateur
    try:
        panier = Panier.objects.get(table=request.user.table, is_active=True)
    except (Panier.DoesNotExist, AttributeError):
        # Si l'utilisateur n'a pas de table ou n'a pas de panier actif
        panier = None
    
    context = {
        'panier': panier,
        'items': panier.items.select_related('plat').all() if panier else [],
        'total': panier.total if panier else Decimal('0.00'),
    }
    return render(request, 'orders/view_cart.html', context)


@role_required(['Rtable', 'Radmin'])
def add_to_cart(request, plat_id):
    plat = get_object_or_404(Plat, id=plat_id, disponible=True)
    
    if request.method == 'POST':
        form = AddToCartForm(request.POST)
        if form.is_valid():
            quantite = form.cleaned_data['quantite']
            notes = form.cleaned_data.get('notes', '')
            
            with transaction.atomic():
                # Récupérer ou créer un panier actif pour la table
                panier, created = Panier.objects.get_or_create(
                    table=request.user.table,
                    is_active=True,
                    defaults={'table': request.user.table}
                )
                
                # Ajouter ou mettre à jour l'article dans le panier
                panier_item, created = PanierItem.objects.get_or_create(
                    panier=panier,
                    plat=plat,
                    defaults={
                        'quantite': quantite,
                        'prix_unitaire': plat.prix_unitaire,
                        'notes': notes,
                    }
                )
                
                if not created:
                    panier_item.quantite = min(panier_item.quantite + quantite, 10)
                    if notes:
                        panier_item.notes = notes
                    panier_item.save()
                
                messages.success(request, f"{quantite}x {plat.nom} ajouté au panier.")
                
                if request.headers.get('HX-Request'):
                    from django.template.loader import render_to_string
                    from django.http import HttpResponse
                    
                    items = panier.items.select_related('plat').all()
                    html = render_to_string('orders/partials/cart_items.html', {
                        'items': items,
                        'total': panier.total
                    })
                    return HttpResponse(html)
                
                return redirect('menu:list_dishes')
    else:
        form = AddToCartForm(initial={'quantite': 1})
    
    return render(request, 'orders/add_to_cart.html', {
        'form': form,
        'plat': plat
    })


@role_required(['Rtable', 'Radmin'])
def update_cart_item(request, item_id):
    item = get_object_or_404(PanierItem, id=item_id, panier__table=request.user.table)
    
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
def remove_from_cart(request, item_id):
    item = get_object_or_404(PanierItem, id=item_id, panier__table=request.user.table)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, "Article retiré du panier.")
        
        if request.headers.get('HX-Request'):
            from django.template.loader import render_to_string
            from django.http import HttpResponse
            
            panier = item.panier
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
    try:
        panier = Panier.objects.get(table=request.user.table, is_active=True)
    except (Panier.DoesNotExist, AttributeError):
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
                    table=request.user.table,
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
                
                # Mettre à jour le statut de la table
                request.user.table.update_status()
                
                messages.success(request, f"Commande {commande.numero_commande} passée avec succès!")
                return redirect('orders:order_confirmation', order_id=commande.id)
    else:
        form = CreateOrderForm()
    
    return render(request, 'orders/create_order.html', {
        'form': form,
        'items': items,
        'total': panier.total
    })


@role_required(['Rtable', 'Radmin'])
def order_confirmation(request, order_id):
    commande = get_object_or_404(Commande, id=order_id, table=request.user.table)
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
def mark_order_paid(request, order_id):
    commande = get_object_or_404(Commande, id=order_id, statut='servie')
    
    if request.method == 'POST':
        commande.statut = 'payee'
        commande.save()
        
        # Créer un nouveau panier vide pour la table
        Panier.objects.create(table=commande.table, is_active=True)
        
        messages.success(request, f"La commande {commande.numero_commande} a été marquée comme payée.")
        return redirect('orders:list_orders')
    
    return render(request, 'orders/mark_order_paid.html', {'commande': commande})


@role_required(['Rtable', 'Radmin'])
def order_history(request):
    commandes = Commande.objects.filter(table=request.user.table).order_by('-date_commande')
    return render(request, 'orders/order_history.html', {'commandes': commandes})
