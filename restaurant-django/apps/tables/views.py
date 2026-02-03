from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from apps.authentication.decorators import role_required
from .models import TableRestaurant
from .forms import TableRestaurantForm


@role_required(['Rservent', 'Radmin'])
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


@role_required(['Rservent', 'Radmin'])
def table_detail(request, table_id):
    table = get_object_or_404(TableRestaurant, id=table_id)
    table.update_status()
    
    commandes = table.commandes.all().order_by('-date_commande').select_related('table')
    
    return render(request, 'tables/table_detail.html', {
        'table': table,
        'commandes': commandes
    })
