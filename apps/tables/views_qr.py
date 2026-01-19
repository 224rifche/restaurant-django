import qrcode
import qrcode.image.svg
from io import BytesIO
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.views import View
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import TableRestaurant
from apps.authentication.models import CustomUser


def is_admin(user):
    return user.is_authenticated and user.role == 'Radmin'


class QRCodeLoginView(View):
    """Vue pour gérer la connexion via QR code"""
    
    def get(self, request, token):
        try:
            table = TableRestaurant.objects.get(qr_token=token)
            
            # Vérifier si la table est bloquée
            if table.is_blocked():
                messages.error(request, "Cette table est actuellement bloquée.")
                return redirect('authentication:login')
            
            # Si l'utilisateur est déjà connecté, on le déconnecte
            if request.user.is_authenticated:
                from django.contrib.auth import logout
                logout(request)
            
            # Récupérer l'utilisateur associé à la table
            user = table.user
            if not user:
                messages.error(request, "Aucun utilisateur n'est associé à cette table.")
                return redirect('authentication:login')

            next_url = (request.GET.get('next') or '').strip()
            url = reverse('authentication:login')
            query = f"?username={user.login}"
            if next_url:
                query += f"&next={next_url}"
            return redirect(f"{url}{query}")
            
        except TableRestaurant.DoesNotExist:
            messages.error(request, "Lien de connexion invalide ou expiré.")
            return redirect('authentication:login')
    
    def post(self, request, token):
        try:
            table = TableRestaurant.objects.get(qr_token=token)
            
            # Vérifier si la table est bloquée
            if table.is_blocked():
                messages.error(request, "Cette table est actuellement bloquée.")
                return redirect('authentication:login')
            
            # Authentifier l'utilisateur
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None and user == table.user:
                login(request, user)
                # Enregistrer les informations de connexion
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
                table.record_login(ip_address)
                
                # Rediriger vers la page d'accueil ou l'URL demandée
                next_url = request.POST.get('next') or 'authentication:redirect_after_login'
                return redirect(next_url)
            else:
                messages.error(request, "Identifiants invalides.")
                return redirect('tables:qr_login', token=token)
                
        except TableRestaurant.DoesNotExist:
            messages.error(request, "Lien de connexion invalide ou expiré.")
            return redirect('authentication:login')


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
    
    # Générer l'URL de connexion
    qr_url = request.build_absolute_uri(reverse('tables:qr_login', kwargs={'token': table.qr_token}))
    
    # Générer le QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_url)
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
