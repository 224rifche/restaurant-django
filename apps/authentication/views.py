from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.db import transaction, IntegrityError
from django.db.models.deletion import ProtectedError
from .forms import CustomLoginForm, CustomUserCreationForm, CustomUserUpdateForm
from .models import CustomUser
from .decorators import role_required


@never_cache
def login_view(request):
    if request.user.is_authenticated:
        return redirect('authentication:redirect_after_login')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_active:
                login(request, user)
                messages.success(request, f'Bienvenue {user.login} — Rôle : {user.get_role_display()}')
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
    elif user.role == 'Rcaissier':
        return redirect('orders:list_orders')
    elif user.role == 'Rcomptable':
        return redirect('payments:dashboard_caisse')
    elif user.role == 'Radmin':
        return redirect('dashboard:home')
    else:
        return redirect('authentication:login')


@login_required
@never_cache
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
            role = form.cleaned_data.get('role')
            table_number = (request.POST.get('table_number') or '').strip()
            seats_raw = (request.POST.get('seats') or '').strip()
            seats = None

            if role == 'Rtable':
                if not table_number:
                    form.add_error(None, "Le numéro de table est obligatoire pour le rôle Table.")
                try:
                    seats = int(seats_raw)
                    if seats < 1:
                        raise ValueError
                except (TypeError, ValueError):
                    form.add_error(None, "Le nombre de places doit être un nombre entier supérieur ou égal à 1.")

                if table_number:
                    from apps.tables.models import TableRestaurant
                    if TableRestaurant.objects.filter(numero_table=table_number).exists():
                        form.add_error(None, "Ce numéro de table existe déjà.")

            if form.errors:
                return render(request, 'authentication/create_user.html', {'form': form})

            try:
                with transaction.atomic():
                    user = form.save()

                    if role == 'Rtable':
                        from apps.tables.models import TableRestaurant
                        TableRestaurant.objects.create(
                            numero_table=table_number,
                            nombre_places=seats,
                            user=user
                        )

                messages.success(request, f'Utilisateur {user.login} créé avec succès.')
                return redirect('authentication:list_users')
            except IntegrityError:
                form.add_error(None, "Erreur lors de la création : ce numéro de table est déjà utilisé.")
                return render(request, 'authentication/create_user.html', {'form': form})
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
            if request.POST.get('force_delete') == '1':
                if user.login == 'system00':
                    messages.error(request, "Vous ne pouvez pas supprimer l'utilisateur système.")
                    return redirect('authentication:list_users')

                def get_system_user():
                    system_user, created = CustomUser.objects.get_or_create(
                        login='system00',
                        defaults={
                            'role': 'Radmin',
                            'is_active': False,
                            'is_staff': False,
                        }
                    )
                    if created:
                        system_user.set_unusable_password()
                        system_user.save(update_fields=['password'])
                    return system_user

                login_to_delete = user.login
                system_user = get_system_user()
                try:
                    with transaction.atomic():
                        from apps.payments.models import Caisse, Paiement, SortieCaisse
                        from apps.expenses.models import Depense
                        from apps.tables.models import TableRestaurant

                        # Mettre à jour les références dans les autres modèles
                        Caisse.objects.filter(utilisateur_ouverture=user).update(utilisateur_ouverture=system_user)
                        Caisse.objects.filter(utilisateur_fermeture=user).update(utilisateur_fermeture=system_user)
                        Paiement.objects.filter(utilisateur=user).update(utilisateur=system_user)
                        SortieCaisse.objects.filter(utilisateur=user).update(utilisateur=system_user)
                        Depense.objects.filter(utilisateur=user).update(utilisateur=system_user)
                        
                        # Mettre à jour les références dans les tables
                        # D'abord récupérer toutes les tables liées à l'utilisateur
                        tables = TableRestaurant.objects.filter(user=user)
                        # Mettre à jour chaque table individuellement
                        for table in tables:
                            table.user = None
                            table.save(update_fields=['user'])

                        # Maintenant, supprimer l'utilisateur
                        user.delete()

                    messages.success(
                        request,
                        f"Utilisateur {login_to_delete} supprimé définitivement. Les historiques ont été réaffectés au compte système."
                    )
                except ProtectedError:
                    messages.error(
                        request,
                        "Suppression définitive impossible : l'utilisateur est encore référencé par d'autres éléments protégés."
                    )
                return redirect('authentication:list_users')

            login_to_delete = user.login
            try:
                user.delete()
                messages.success(request, f'Utilisateur {login_to_delete} supprimé avec succès.')
            except ProtectedError:
                user.is_active = False
                user.save(update_fields=['is_active'])
                messages.warning(
                    request,
                    "Impossible de supprimer cet utilisateur car il est lié à des opérations (caisse/paiements/dépenses). "
                    "Le compte a été désactivé à la place."
                )
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
