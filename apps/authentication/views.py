from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .forms import CustomLoginForm, CustomUserCreationForm, CustomUserUpdateForm
from .models import CustomUser
from .decorators import role_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect('authentication:redirect_after_login')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_active:
                login(request, user)
                messages.success(request, f'Bienvenue {user.login}!')
                return redirect('authentication:redirect_after_login')
            else:
                messages.error(request, 'Votre compte est désactivé.')
        else:
            messages.error(request, 'Login ou mot de passe incorrect.')
    else:
        form = CustomLoginForm()
    
    return render(request, 'authentication/login.html', {'form': form})


@login_required
def redirect_after_login(request):
    user = request.user
    
    if user.role == 'Rtable':
        return redirect('menu:list_dishes')
    elif user.role == 'Rservent':
        return redirect('tables:list_tables')
    elif user.role == 'Rcuisinier':
        return redirect('menu:manage_dishes')
    elif user.role == 'Rcomptable':
        return redirect('payments:dashboard_caisse')
    elif user.role == 'Radmin':
        return redirect('dashboard:home')
    else:
        return redirect('authentication:login')


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('authentication:login')


@role_required(['Radmin'])
def list_users(request):
    users = CustomUser.objects.all().order_by('role', 'login')
    return render(request, 'authentication/list_users.html', {'users': users})


@role_required(['Radmin'])
def create_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                
                if user.role == 'Rtable':
                    from apps.tables.models import TableRestaurant
                    table_number = request.POST.get('table_number')
                    seats = request.POST.get('seats', 4)
                    
                    if table_number:
                        TableRestaurant.objects.create(
                            numero_table=table_number,
                            nombre_places=seats,
                            user=user
                        )
                
                messages.success(request, f'Utilisateur {user.login} créé avec succès.')
                return redirect('authentication:list_users')
        else:
            messages.error(request, 'Erreur lors de la création de l\'utilisateur.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'authentication/create_user.html', {'form': form})


@role_required(['Radmin'])
def update_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Utilisateur {user.login} modifié avec succès.')
            return redirect('authentication:list_users')
    else:
        form = CustomUserUpdateForm(instance=user)
    
    return render(request, 'authentication/update_user.html', {'form': form, 'user': user})


@role_required(['Radmin'])
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        if user == request.user:
            messages.error(request, 'Vous ne pouvez pas supprimer votre propre compte.')
        else:
            login_to_delete = user.login
            user.delete()
            messages.success(request, f'Utilisateur {login_to_delete} supprimé avec succès.')
        return redirect('authentication:list_users')
    
    return render(request, 'authentication/delete_user.html', {'user': user})


@role_required(['Radmin'])
def toggle_user_status(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    
    if user == request.user:
        messages.error(request, 'Vous ne pouvez pas désactiver votre propre compte.')
    else:
        user.is_active = not user.is_active
        user.save()
        status = 'activé' if user.is_active else 'désactivé'
        messages.success(request, f'Utilisateur {user.login} {status} avec succès.')
    
    return redirect('authentication:list_users')
