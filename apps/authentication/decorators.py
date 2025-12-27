from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden


def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('authentication:login')
            
            if not request.user.is_active:
                messages.error(request, "Votre compte est désactivé.")
                return redirect('authentication:login')
            
            if request.user.role not in allowed_roles:
                messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
                return HttpResponseForbidden("Accès refusé")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
