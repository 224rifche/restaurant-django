from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.authentication.decorators import role_required
from django.db.models import Q
from .models import Plat, CategoriePlat
from .forms import PlatForm


@role_required(['Rtable', 'Radmin'])
def list_dishes(request):
    categories = list(CategoriePlat.objects.order_by('ordre', 'nom').values_list('nom', flat=True))
    q = (request.GET.get('q') or '').strip()
    cat = (request.GET.get('cat') or '').strip()
    plats = Plat.objects.filter(disponible=True)
    if cat and (not categories or cat in categories):
        plats = plats.filter(categorie=cat)
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
            messages.success(request, f'Plat "{plat.nom}" créé avec succès.')
            return redirect('menu:manage_dishes')
    else:
        form = PlatForm()
    
    return render(request, 'menu/create_dish.html', {'form': form})


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
    
    return render(request, 'menu/update_dish.html', {'form': form, 'plat': plat})


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
        plat.delete()
        messages.success(request, f'Plat "{nom}" supprimé avec succès.')
        return redirect('menu:manage_dishes')
    
    return render(request, 'menu/delete_dish.html', {'plat': plat})
