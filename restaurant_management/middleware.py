import os
from django.conf import settings
from django.http import HttpResponse, Http404
from django.utils.http import http_date
from django.core.files.storage import default_storage

class MediaMiddleware:
    """
    Middleware pour servir les fichiers médias en production quand USE_S3=False
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.media_url = settings.MEDIA_URL.rstrip('/')
        self.media_root = getattr(settings, 'MEDIA_ROOT', None)
        
    def __call__(self, request):
        # Ne s'activer qu'en production et sans S3
        if (not getattr(settings, 'DEBUG', True) and 
            not getattr(settings, 'USE_S3', False) and 
            request.path.startswith(self.media_url)):
            return self.serve_media_file(request)
        
        response = self.get_response(request)
        return response
    
    def serve_media_file(self, request):
        """Servir un fichier média"""
        try:
            # Extraire le chemin du fichier
            file_path = request.path[len(self.media_url):].lstrip('/')
            
            # Sécurité : vérifier que le chemin ne remonte pas dans l'arborescence
            if '..' in file_path or file_path.startswith('/'):
                raise Http404()
            
            # Construire le chemin complet
            full_path = os.path.join(self.media_root, file_path)
            
            # Vérifier que le fichier existe et est un fichier régulier
            if not os.path.exists(full_path) or not os.path.isfile(full_path):
                raise Http404()
            
            # Vérifier que le chemin est bien dans media_root (sécurité)
            if not os.path.abspath(full_path).startswith(os.path.abspath(self.media_root)):
                raise Http404()
            
            # Lire le fichier
            with open(full_path, 'rb') as f:
                content = f.read()
            
            # Déterminer le type MIME
            content_type = self.get_content_type(file_path)
            
            # Créer la réponse
            response = HttpResponse(content, content_type=content_type)
            
            # Headers pour le cache et la sécurité
            response['Last-Modified'] = http_date(os.path.getmtime(full_path))
            response['Cache-Control'] = 'public, max-age=31536000'  # 1 an
            response['X-Content-Type-Options'] = 'nosniff'
            
            return response
            
        except Http404:
            raise
        except Exception as e:
            # En cas d'erreur, logger et retourner 404
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erreur lors de la lecture du média {request.path}: {e}")
            raise Http404(f"Fichier média non trouvé")
    
    def get_content_type(self, file_path):
        """Déterminer le type MIME du fichier"""
        ext = os.path.splitext(file_path)[1].lower()
        
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.avif': 'image/avif',
            '.svg': 'image/svg+xml',
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.ico': 'image/x-icon',
        }
        
        return content_types.get(ext, 'application/octet-stream')
