from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse


def role_required(allowed_roles):
    """
    Vérifie que l'utilisateur connecté a l'un des rôles autorisés.
    Redirige vers la page de connexion ou le tableau de bord approprié en cas d'échec.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "Veuillez vous connecter pour accéder à cette page.")
                return redirect(f"{reverse('authentication:login')}?next={request.path}")
            
            if not request.user.is_active:
                messages.error(request, "Votre compte est désactivé.")
                return redirect('authentication:login')
            
            if request.user.role not in allowed_roles:
                messages.error(
                    request, 
                    f"Accès refusé. Rôle requis : {', '.join(allowed_roles)}. "
                    f"Votre rôle : {request.user.get_role_display()}"
                )
                # Rediriger vers le tableau de bord approprié selon le rôle
                if hasattr(request.user, 'role'):
                    return redirect('authentication:redirect_after_login')
                return redirect('authentication:login')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
