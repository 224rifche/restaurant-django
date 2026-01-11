from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from apps.authentication.decorators import role_required
from apps.menu.models import Plat, CategoriePlat
from apps.orders.models import Panier, PanierItem, Commande, CommandeItem
from .models import TableRestaurant
from .forms import TableRestaurantForm


@role_required(['Rservent', 'Radmin', 'Rcaissier'])
def list_tables(request):
    tables = TableRestaurant.objects.all().select_related('user')
    
    for table in tables:
        table.update_status()
    
    return render(request, 'tables/list_tables.html', {'tables': tables})


@role_required(['Radmin'])
def create_table(request):
    if request.method == 'POST':
        form = TableRestaurantForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Table créée avec succès.')
            return redirect('tables:list_tables')
    else:
        form = TableRestaurantForm()
    
    return render(request, 'tables/create_table.html', {'form': form})


@role_required(['Radmin'])
def update_table(request, table_id):
    table = get_object_or_404(TableRestaurant, id=table_id)
    
    if request.method == 'POST':
        form = TableRestaurantForm(request.POST, instance=table)
        if form.is_valid():
            form.save()
            messages.success(request, f'Table {table.numero_table} modifiée avec succès.')
            return redirect('tables:list_tables')
    else:
        form = TableRestaurantForm(instance=table)
    
    return render(request, 'tables/update_table.html', {'form': form, 'table': table})


@role_required(['Radmin'])
def delete_table(request, table_id):
    table = get_object_or_404(TableRestaurant, id=table_id)
    
    if request.method == 'POST':
        numero = table.numero_table
        table.delete()
        messages.success(request, f'Table {numero} supprimée avec succès.')
        return redirect('tables:list_tables')
    
    return render(request, 'tables/delete_table.html', {'table': table})


@role_required(['Rservent', 'Radmin', 'Rcaissier'])
@transaction.atomic
def table_detail(request, table_id):
    table = get_object_or_404(TableRestaurant, id=table_id)
    table.update_status()

    def _redirect_back():
        return redirect(request.META.get('HTTP_REFERER') or 'tables:table_detail', table_id=table.id)

    # Gestion des paniers actifs multiples
    paniers_actifs = Panier.objects.filter(table=table, is_active=True).order_by('-created_at')
    if paniers_actifs.count() > 1:
        # Garder uniquement le plus récent actif
        panier = paniers_actifs.first()
        paniers_actifs.exclude(id=panier.id).update(is_active=False)
    elif paniers_actifs.exists():
        panier = paniers_actifs.first()
    else:
        # Créer un nouveau panier si aucun n'existe
        panier = Panier.objects.create(
            table=table,
            created_by=request.user,
            is_active=True
        )
    
    # Action: ajouter un plat au panier
    if request.method == 'POST' and 'add_plat' in request.POST:
        plat_id = request.POST.get('plat_id')
        quantite = request.POST.get('quantite')
        try:
            quantite_int = int(quantite) if quantite else 1
        except ValueError:
            quantite_int = 1

        plat = get_object_or_404(Plat, id=plat_id, disponible=True)
        item, created = PanierItem.objects.get_or_create(
            panier=panier,
            plat=plat,
            defaults={
                'quantite': max(1, min(10, quantite_int)),
                'prix_unitaire': plat.prix_unitaire,
            }
        )
        if not created:
            item.quantite = max(1, min(10, item.quantite + max(1, min(10, quantite_int))))
            item.save()

        messages.success(request, f"{plat.nom} ajouté au panier.")
        return _redirect_back()

    # Action: mise à jour du nombre de clients
    if request.method == 'POST' and 'set_clients' in request.POST:
        raw = (request.POST.get('nombre_clients_actuels') or '').strip()
        try:
            value = int(raw)
        except ValueError:
            value = None

        if value is None or value < 0:
            messages.error(request, "Nombre de clients invalide.")
            return _redirect_back()

        table.nombre_clients_actuels = value
        table.save(update_fields=['nombre_clients_actuels'])
        messages.success(request, "Nombre de clients mis à jour.")
        return _redirect_back()

    # Action: supprimer un item du panier
    if request.method == 'POST' and 'remove_item' in request.POST:
        item_id = request.POST.get('item_id')
        item = get_object_or_404(PanierItem, id=item_id, panier=panier)
        item.delete()
        messages.success(request, 'Article supprimé du panier.')
        return _redirect_back()

    # Action: annuler la commande en cours (vider/désactiver le panier)
    if request.method == 'POST' and 'annuler_panier' in request.POST:
        panier.items.all().delete()
        panier.is_active = False
        panier.save()
        Panier.objects.create(
            table=table,
            created_by=request.user,
            is_active=True
        )
        messages.success(request, 'Commande annulée.')
        return _redirect_back()

    # Récupérer les articles du panier
    panier_items = panier.items.select_related('plat').all()
    
    # Gérer la soumission du formulaire de commande
    if request.method == 'POST' and 'commander' in request.POST:
        if panier_items.exists():
            with transaction.atomic():
                # Créer la commande
                commande = Commande.objects.create(
                    table=table,
                    montant_total=panier.total,
                    statut='en_attente',
                    serveur=request.user
                )
                
                # Ajouter les articles à la commande
                for item in panier_items:
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
                return redirect('orders:view_order', order_id=commande.id)
        else:
            messages.warning(request, 'Le panier est vide!')
    
    # Récupérer les commandes récentes
    commandes = table.commandes.all().order_by('-date_commande')[:5]
    
    # Récupérer les plats disponibles (filtre catégorie + recherche)
    categories = list(CategoriePlat.objects.order_by('ordre', 'nom').values_list('nom', flat=True))
    if not categories:
        categories = ['Poulet', 'Jus', 'Viande', 'Poisson', 'Chawarma']
    cat = (request.GET.get('cat') or '').strip()
    q = (request.GET.get('q') or '').strip()
    plats = Plat.objects.filter(disponible=True)
    if cat and cat in categories:
        plats = plats.filter(categorie=cat)
    if q:
        plats = plats.filter(Q(nom__icontains=q) | Q(description__icontains=q))
    plats = plats.order_by('nom')
    
    return render(request, 'tables/table_detail.html', {
        'table': table,
        'panier': panier,
        'panier_items': panier_items,
        'commandes': commandes,
        'plats': plats,
        'categories': categories,
        'selected_cat': cat if cat in categories else '',
        'q': q,
    })
