from django.shortcuts import redirect
from django.urls import reverse, resolve
from django.contrib import messages
from django.contrib.auth import logout
from django.http import Http404


class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_urls = [
            reverse('authentication:login'),
            reverse('authentication:logout'),
            reverse('authentication:redirect_after_login'),
            '/admin/',
            '/static/',
            '/media/',
            '/favicon.ico',
            '/',
            '/login/',
            '/redirect/',
        ]
        # Définir les URLs accessibles par chaque rôle (selon le cahier des charges)
        self.role_allowed_urls = {
            'Radmin': ['*'],  # Accès total à toutes les fonctionnalités
            'Rcomptable': [
                '/dashboard/',      # Tableau de bord
                '/payments/',       # Consultation paiements et caisse
                '/expenses/',       # Enregistrement des dépenses
            ],
            'Rcuisinier': [
                '/menu/manage/',    # Gestion des plats (ajouter, modifier, activer/désactiver)
                '/menu/create/',
                '/menu/update/',
                '/menu/toggle/',
            ],
            'Rservent': [
                '/tables/',         # Visualisation des tables
                '/orders/',         # Gestion des commandes (servir, paiement)
                '/payments/paiement/',  # Enregistrer les paiements
            ],
            'Rtable': [
                '/menu/',           # Consultation des plats
                '/orders/cart/',    # Gestion du panier
                '/orders/add/',     # Ajout au panier
                '/orders/update/',  # Modification panier
                '/orders/remove/',  # Suppression du panier
                '/orders/create/',  # Validation commande
                '/orders/confirmation/', # Confirmation commande
                '/orders/history/', # Historique des commandes
            ]
        }

    def __call__(self, request):
        # Vérifier si l'URL est exemptée
        if any(request.path.startswith(url) for url in self.exempt_urls):
            return self.get_response(request)

        # Gestion des utilisateurs non authentifiés
        if not request.user.is_authenticated:
            return redirect(f"{reverse('authentication:login')}?next={request.path}")
        
        # Vérifier si le compte est actif
        if not request.user.is_active:
            logout(request)
            messages.error(request, "Votre compte est désactivé.")
            return redirect('authentication:login')

        # Vérifier les permissions basées sur le rôle
        if not self.has_permission(request):
            messages.error(
                request,
                f"Vous n'avez pas la permission d'accéder à cette page. "
                f"Rôle requis : {', '.join(self.get_required_roles(request))}"
            )
            return redirect('authentication:redirect_after_login')

        return self.get_response(request)

    def has_permission(self, request):
        """Vérifie si l'utilisateur a la permission d'accéder à l'URL demandée"""
        user_role = request.user.role if hasattr(request.user, 'role') else None
        
        # L'administrateur a accès à tout
        if user_role == 'Radmin':
            return True
            
        # Récupérer les URLs autorisées pour le rôle de l'utilisateur
        allowed_urls = self.role_allowed_urls.get(user_role, [])
        
        # Vérifier si l'URL actuelle correspond à un motif autorisé
        for url_pattern in allowed_urls:
            if url_pattern == '*':
                return True
            if request.path.startswith(url_pattern):
                return True
                
        return False

    def get_required_roles(self, request):
        """Retourne les rôles requis pour accéder à l'URL demandée"""
        required_roles = []
        for role, urls in self.role_allowed_urls.items():
            for url_pattern in urls:
                if url_pattern == '*' and request.path.startswith('/'):
                    required_roles.append(role)
                    break
                if request.path.startswith(url_pattern):
                    required_roles.append(role)
                    break
        return required_roles if required_roles else ['Aucun rôle spécifique']
