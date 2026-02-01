from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.authentication.decorators import role_required
from django.db.models import Q
from .models import Plat, CategoriePlat
from .forms import PlatForm, CategoriePlatForm


@role_required(['Rtable', 'Radmin'])
def list_dishes(request):
    categories = list(CategoriePlat.objects.order_by('ordre', 'nom').values_list('nom', flat=True))
    q = (request.GET.get('q') or '').strip()
    cat = (request.GET.get('cat') or '').strip()
    plats = Plat.objects.filter(disponible=True)
    if cat and (not categories or cat in categories):
        # Filtrer par nom de catégorie via la foreign key
        plats = plats.filter(categorie__nom=cat)
    if q:
        plats = plats.filter(Q(nom__icontains=q) | Q(description__icontains=q))
    plats = plats.order_by('nom')
    return render(request, 'menu/list_dishes.html', {
        'plats': plats,
        'q': q,
        'categories': categories,
        'selected_cat': cat,
    })


@role_required(['Rcuisinier', 'Radmin'])
def manage_dishes(request):
    plats = Plat.objects.all().order_by('nom')
    return render(request, 'menu/manage_dishes.html', {'plats': plats})


@role_required(['Rcuisinier', 'Radmin'])
def create_dish(request):
    if request.method == 'POST':
        form = PlatForm(request.POST, request.FILES)
        if form.is_valid():
            plat = form.save()
            plat.save()
            messages.success(request, f'Plat "{plat.nom}" créé avec succès.')
            return redirect('menu:manage_dishes')
    else:
        form = PlatForm()

    categories = list(CategoriePlat.objects.order_by('ordre', 'nom').values_list('nom', flat=True))
    return render(request, 'menu/create_dish.html', {'form': form, 'categories': categories})


@role_required(['Rcuisinier', 'Radmin'])
def update_dish(request, dish_id):
    plat = get_object_or_404(Plat, id=dish_id)
    
    if request.method == 'POST':
        form = PlatForm(request.POST, request.FILES, instance=plat)
        if form.is_valid():
            form.save()
            messages.success(request, f'Plat "{plat.nom}" modifié avec succès.')
            return redirect('menu:manage_dishes')
    else:
        form = PlatForm(instance=plat)

    categories = list(CategoriePlat.objects.order_by('ordre', 'nom').values_list('nom', flat=True))
    return render(request, 'menu/update_dish.html', {'form': form, 'plat': plat, 'categories': categories})


@role_required(['Rcuisinier', 'Radmin'])
def toggle_dish_availability(request, dish_id):
    plat = get_object_or_404(Plat, id=dish_id)
    plat.disponible = not plat.disponible
    plat.save()
    
    status = 'activé' if plat.disponible else 'désactivé'
    messages.success(request, f'Plat "{plat.nom}" {status} avec succès.')
    return redirect('menu:manage_dishes')


@role_required(['Radmin'])
def delete_dish(request, dish_id):
    plat = get_object_or_404(Plat, id=dish_id)
    
    if request.method == 'POST':
        nom = plat.nom
        
        try:
            # Vérifier si le plat est référencé dans des paniers ou commandes
            from apps.orders.models import PanierItem, CommandeItem
            
            panier_items = PanierItem.objects.filter(plat=plat)
            commande_items = CommandeItem.objects.filter(plat=plat)
            
            if panier_items.exists() or commande_items.exists():
                # Marquer le plat comme non disponible au lieu de le supprimer
                plat.disponible = False
                plat.save()
                
                # Compter les références pour le message
                panier_count = panier_items.count()
                commande_count = commande_items.count()
                
                messages.warning(request, 
                    f'Le plat "{nom}" ne peut pas être supprimé car il est utilisé dans '
                    f'{panier_count} panier(s) et {commande_count} commande(s). '
                    f'Il a été marqué comme non disponible à la place.')
            else:
                # Supprimer le plat s'il n'est pas référencé
                plat.delete()
                messages.success(request, f'Plat "{nom}" supprimé avec succès.')
                
        except Exception as e:
            messages.error(request, f'Erreur lors de la suppression du plat: {str(e)}')
        
        return redirect('menu:manage_dishes')
    
    return render(request, 'menu/delete_dish.html', {'plat': plat})


@role_required(['Rcuisinier', 'Radmin'])
def manage_categories(request):
    categories = CategoriePlat.objects.all().order_by('ordre', 'nom')
    return render(request, 'menu/manage_categories.html', {'categories': categories})


@role_required(['Rcuisinier', 'Radmin'])
def create_category(request):
    if request.method == 'POST':
        form = CategoriePlatForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Catégorie "{category.nom}" créée avec succès.')
            return redirect('menu:manage_categories')
    else:
        form = CategoriePlatForm()
    return render(request, 'menu/create_category.html', {'form': form})


@role_required(['Rcuisinier', 'Radmin'])
def update_category(request, category_id):
    category = get_object_or_404(CategoriePlat, id=category_id)
    if request.method == 'POST':
        form = CategoriePlatForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Catégorie "{category.nom}" modifiée avec succès.')
            return redirect('menu:manage_categories')
    else:
        form = CategoriePlatForm(instance=category)
    return render(request, 'menu/update_category.html', {'form': form, 'category': category})


@role_required(['Radmin'])
def delete_category(request, category_id):
    category = get_object_or_404(CategoriePlat, id=category_id)
    if request.method == 'POST':
        nom = category.nom
        category.delete()
        messages.success(request, f'Catégorie "{nom}" supprimée avec succès.')
        return redirect('menu:manage_categories')
    return render(request, 'menu/delete_category.html', {'category': category})
