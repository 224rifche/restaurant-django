import qrcode
import qrcode.image.svg
from io import BytesIO
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.views import View
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import TableRestaurant
from apps.authentication.models import CustomUser


def is_admin(user):
    return user.is_authenticated and user.role == 'Radmin'


def get_client_ip(request):
    """Récupère l'adresse IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class QRCodeLoginView(View):
    """Vue pour la connexion automatique via QR code"""
    
    def get(self, request, token):
        """Connexion automatique et redirection vers la prise de commande"""
        try:
            table = TableRestaurant.objects.get(qr_token=token)
        except TableRestaurant.DoesNotExist:
            messages.error(request, "QR Code invalide ou expiré.")
            return redirect('authentication:login')
        
        # Vérifier si la table est bloquée
        if table.is_blocked():
            messages.error(request, f"La table {table.numero_table} est actuellement bloquée.")
            return redirect('authentication:login')
        
        # Vérifier si la table a un utilisateur associé
        if not table.user:
            messages.error(request, f"Aucun utilisateur n'est associé à la table {table.numero_table}.")
            return redirect('authentication:login')
        
        # Connexion automatique de l'utilisateur
        user = table.user
        
        # Enregistrer l'IP et la date de connexion
        ip_address = get_client_ip(request)
        table.record_login(ip_address)
        
        # Connecter l'utilisateur automatiquement
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        
        # Créer automatiquement un panier pour cette table s'il n'en existe pas
        from apps.orders.models import Panier
        existing_panier = Panier.objects.filter(table=table, is_active=True).first()
        if not existing_panier:
            Panier.objects.create(
                table=table,
                created_by=user,
                is_active=True
            )
        
        # Message de bienvenue
        messages.success(request, f"Bienvenue à la table {table.numero_table} !")
        
        # Rediriger directement vers le menu pour prendre des commandes
        return redirect('menu:list_dishes')
    
    def post(self, request, token):
        """Pour compatibilité, mais GET est maintenant utilisé pour la connexion automatique"""
        return self.get(request, token)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class QRCodeAdminView(TemplateView):
    """Vue pour l'administration des QR codes"""
    template_name = 'tables/admin/qr_codes.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tables'] = TableRestaurant.objects.all().order_by('numero_table')
        return context


@login_required
@user_passes_test(is_admin)
def generate_qr_code(request, table_id, download=False):
    """Génère un nouveau QR code pour une table
    
    Args:
        request: La requête HTTP
        table_id: L'ID de la table
        download: Si True, force le téléchargement du QR code. Si False, l'affiche dans le navigateur.
    """
    table = get_object_or_404(TableRestaurant, id=table_id)
    
    # Vérifier que la table a un utilisateur associé
    if not table.user:
        messages.error(request, f"Aucun utilisateur n'est associé à la table {table.numero_table}.")
        return redirect('tables:qr_admin')
    
    # Générer un nouveau token si nécessaire
    if not table.qr_token:
        table.generate_qr_token()
    
    # Construire l'URL complète pour le QR code
    qr_login_url = table.get_qr_code_url(request)
    
    # Générer le QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_login_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Sauvegarder l'image dans un buffer
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Créer la réponse avec l'image
    response = HttpResponse(buffer, content_type='image/png')

    # Si download=True ou si c'est une requête AJAX, forcer le téléchargement
    download_param = (request.GET.get('download') or '').strip().lower()
    download_from_query = download_param in {'1', 'true', 'yes'}

    if download or download_from_query or request.headers.get('x-requested-with') == 'XMLHttpRequest':
        response['Content-Disposition'] = f'attachment; filename=qr_table_{table.numero_table}.png'
    else:
        # Sinon, afficher dans le navigateur
        response['Content-Disposition'] = f'inline; filename=qr_table_{table.numero_table}.png'
    
    return response


@login_required
@user_passes_test(is_admin)
def view_qr_code(request, table_id):
    """Affiche une page avec le QR code de la table"""
    table = get_object_or_404(TableRestaurant, id=table_id)
    if not table.qr_token:
        table.generate_qr_token()
    
    qr_url = reverse('tables:table_generate_qr_code', kwargs={'table_id': table.id})
    download_url = f"{qr_url}?download=1"
    
    return render(request, 'tables/qr_code_display.html', {
        'table': table,
        'qr_url': qr_url,
        'download_url': download_url,
    })


@login_required
@user_passes_test(is_admin)
def toggle_table_status(request, table_id):
    """Active ou désactive une table"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return JsonResponse({'error': 'Requête invalide'}, status=400)
    
    table = get_object_or_404(TableRestaurant, id=table_id)
    
    if table.qr_status == 'blocked':
        table.unblock()
        status = 'active'
    else:
        table.block()
        status = 'blocked'
    
    return JsonResponse({
        'status': 'success',
        'new_status': status,
        'status_display': table.get_qr_status_display()
    })


@login_required
@user_passes_test(is_admin)
@require_POST
def invalidate_all_table_qr_tokens(request):
    TableRestaurant.objects.update(qr_token=None, qr_status='inactive')
    messages.success(request, "QR codes invalidés pour toutes les tables.")
    return redirect('tables:qr_admin')