from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
import os
 
def error_404_view(request, exception=None):
    return render(request, '404.html', {'requested_path': request.path}, status=404)

def media_diagnostic(request):
    """Vue pour diagnostiquer les problèmes de médias"""
    
    context = {
        'debug': settings.DEBUG,
        'use_s3': getattr(settings, 'USE_S3', False),
        'media_root': getattr(settings, 'MEDIA_ROOT', None),
        'media_url': getattr(settings, 'MEDIA_URL', None),
        'whitenoise_root': getattr(settings, 'WHITENOISE_ROOT', None),
    }
    
    # Vérifier si le dossier media existe
    if context['media_root']:
        context['media_root_exists'] = os.path.exists(context['media_root'])
        context['media_root_readable'] = os.access(context['media_root'], os.R_OK) if context['media_root_exists'] else False
        
        # Lister les fichiers dans media/plats
        plats_dir = os.path.join(context['media_root'], 'plats')
        if os.path.exists(plats_dir):
            context['plats_files'] = os.listdir(plats_dir)[:10]  # Limiter à 10 fichiers
        else:
            context['plats_files'] = []
    
    # Tester les URLs
    if request.GET.get('test_urls'):
        from apps.menu.models import Plat
        plats_with_images = Plat.objects.exclude(image='').exclude(image__isnull=True)[:3]
        test_urls = []
        for plat in plats_with_images:
            if plat.image:
                test_urls.append({
                    'plat': plat.nom,
                    'image_path': plat.image.name,
                    'image_url': plat.image.url if plat.image else None,
                })
        context['test_urls'] = test_urls
    
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse(context)
    
    return render(request, 'diagnostic/media_diagnostic.html', context)
