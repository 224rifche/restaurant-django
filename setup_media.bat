@echo off
REM Script de configuration des médias pour la production (Windows)

echo 🔧 Configuration des médias pour la production...

REM Créer les dossiers nécessaires
echo 📁 Création des dossiers médias...
if not exist "media" mkdir media
if not exist "media\plats" mkdir media\plats
if not exist "media\justificatifs" mkdir media\justificatifs
if not exist "media\depenses" mkdir media\depenses

REM Collecter les fichiers statiques
echo 📦 Collecte des fichiers statiques...
python manage.py collectstatic --noinput

REM Vérifier la configuration
echo 🔍 Diagnostic de la configuration...
python manage.py shell -c "
from django.conf import settings
import os
print(f'DEBUG: {settings.DEBUG}')
print(f'USE_S3: {getattr(settings, \"USE_S3\", False)}')
print(f'MEDIA_ROOT: {settings.MEDIA_ROOT}')
print(f'MEDIA_URL: {settings.MEDIA_URL}')
print(f'WHITENOISE_ROOT: {getattr(settings, \"WHITENOISE_ROOT\", \"Non défini\")}')

if os.path.exists(settings.MEDIA_ROOT):
    print(f'✅ MEDIA_ROOT existe: {settings.MEDIA_ROOT}')
    print(f'📁 Contenu: {os.listdir(settings.MEDIA_ROOT)}')
else:
    print(f'❌ MEDIA_ROOT n\\'existe pas: {settings.MEDIA_ROOT}')
"

echo ✅ Configuration des médias terminée!
echo 🌐 Accédez au diagnostic: /diagnostic/media/
