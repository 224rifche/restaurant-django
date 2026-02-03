from storages.backends.s3boto3 import S3Boto3Storage
from django.core.files.storage import default_storage
import logging

logger = logging.getLogger(__name__)

class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = False
    # Désactiver les vérifications HeadObject pour éviter les erreurs 403
    querystring_auth = False
    custom_domain = False
    # Ne pas vérifier l'existence des fichiers avant de sauvegarder
    file_overwrite = False
    # Désactiver la validation de l'existence des fichiers
    def get_valid_name(self, name):
        return name
    def get_available_name(self, name, max_length=None):
        return name
    
    def save(self, name, content, max_length=None):
        try:
            return super().save(name, content, max_length)
        except Exception as e:
            logger.error(f"Erreur S3 lors de la sauvegarde de {name}: {e}")
            # Fallback vers le stockage local
            from django.conf import settings
            if hasattr(settings, 'MEDIA_ROOT'):
                import os
                local_path = os.path.join(settings.MEDIA_ROOT, name)
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                with open(local_path, 'wb') as f:
                    f.write(content.read())
                return name
            raise
    
    def delete(self, name):
        try:
            return super().delete(name)
        except Exception as e:
            logger.error(f"Erreur S3 lors de la suppression de {name}: {e}")
            # Ne pas bloquer l'opération si S3 échoue
            return False
    
    def exists(self, name):
        try:
            return super().exists(name)
        except Exception as e:
            logger.error(f"Erreur S3 lors de la vérification de {name}: {e}")
            return False