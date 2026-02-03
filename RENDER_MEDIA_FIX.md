# 🚨 Problème identifié : Images 404 sur Render.com

## Analyse des logs
```
GET /media/plats/134099780150277525.jpg HTTP/1.1" 404 1208
GET /media/plats/776967.jpg HTTP/1.1" 404 1208
```

Les images retournent 404 car la configuration de production n'est pas correcte sur Render.com.

## 🔧 Solution immédiate pour Render.com

### Étape 1: Variables d'environnement sur Render

Dans le dashboard Render.com, ajoutez ces variables d'environnement :

```bash
DEBUG=False
USE_S3=False
ALLOWED_HOSTS=restaurant-django-6ty1.onrender.com,.onrender.com,localhost,127.0.0.1
SECRET_KEY=votre-clé-secrète-ici
```

### Étape 2: Configurer S3 (recommandé pour Render)

Render.com n'est pas idéal pour servir les fichiers locaux. La meilleure solution est S3 :

```bash
# Variables d'environnement S3 sur Render
USE_S3=True
AWS_ACCESS_KEY_ID=votre-access-key
AWS_SECRET_ACCESS_KEY=votre-secret-key
AWS_STORAGE_BUCKET_NAME=votre-bucket-nom
AWS_S3_REGION_NAME=us-east-1
AWS_S3_CUSTOM_DOMAIN=votre-bucket.s3.amazonaws.com
```

### Étape 3: Alternative si pas de S3

Si vous ne voulez pas utiliser S3, modifiez la configuration pour Render :

```python
# Dans settings.py - ajouter après la configuration existante
import os

if 'RENDER' in os.environ:
    # Configuration spécifique pour Render
    DEBUG = False
    USE_S3 = False
    
    # Servir les médias avec Django (non recommandé pour la production)
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
        'restaurant_management.middleware.MediaMiddleware',
    ] + MIDDLEWARE[1:]
    
    # Configuration des URLs pour Render
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
```

## 🎯 Solution rapide (pour tester)

### Option 1: Diagnostic
Accédez à : https://restaurant-django-6ty1.onrender.com/diagnostic/media/

### Option 2: Test manuel
Accédez à : https://restaurant-django-6ty1.onrender.com/media/test_simple.txt

## 📋 Pourquoi ça ne fonctionne pas

1. **DEBUG=True** en local mais **DEBUG=False** requis en production
2. **USE_S3** probablement True sur Render mais pas configuré
3. **ALLOWED_HOSTS** ne contient pas le domaine Render
4. Les fichiers médias ne sont pas uploadés sur Render

## 🚀 Solution recommandée

### Utiliser S3 (meilleure pratique)

1. **Créer un bucket S3**
2. **Configurer les variables d'environnement** sur Render
3. **Uploader les médias existants** vers S3

### Script pour uploader les médias vers S3

```python
# upload_media_to_s3.py
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_management.settings')
django.setup()

from django.core.files.storage import default_storage
from apps.menu.models import Plat

plats = Plat.objects.exclude(image='').exclude(image__isnull=True)
for plat in plats:
    if plat.image and hasattr(plat.image, 'path'):
        with open(plat.image.path, 'rb') as f:
            default_storage.save(f'media/plats/{plat.image.name.split("/")[-1]}', f)
        print(f"Uploadé: {plat.image.name}")
```

## ⚡ Solution immédiate (temporaire)

Ajoutez ces variables sur Render.com :

```bash
DEBUG=False
USE_S3=False
ALLOWED_HOSTS=restaurant-django-6ty1.onrender.com,.onrender.com
```

Puis redéployez l'application.

## 🔍 Vérification

Après configuration, testez :
1. https://restaurant-django-6ty1.onrender.com/diagnostic/media/
2. Les URLs des images dans le gestionnaire de menu

## 💡 Conseil

Pour la production, **S3 est fortement recommandé** car :
- Les fichiers sont persistants
- Meilleures performances
- CDN intégré
- Scalabilité

Render.com peut recréer les conteneurs, donc les fichiers locaux peuvent être perdus.
