#!/bin/bash

# Script de configuration des médias pour la production

echo "🔧 Configuration des médias pour la production..."

# Créer les dossiers nécessaires
echo "📁 Création des dossiers médias..."
mkdir -p media/plats
mkdir -p media/justificatifs
mkdir -p media/depenses

# Vérifier les permissions
echo "🔐 Vérification des permissions..."
chmod 755 media
chmod 755 media/plats
chmod 755 media/justificatifs
chmod 755 media/depenses

# Collecter les fichiers statiques
echo "📦 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# Vérifier la configuration
echo "🔍 Diagnostic de la configuration..."
python manage.py shell << EOF
from django.conf import settings
print(f"DEBUG: {settings.DEBUG}")
print(f"USE_S3: {getattr(settings, 'USE_S3', False)}")
print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"MEDIA_URL: {settings.MEDIA_URL}")
print(f"WHITENOISE_ROOT: {getattr(settings, 'WHITENOISE_ROOT', 'Non défini')}")

import os
if os.path.exists(settings.MEDIA_ROOT):
    print(f"✅ MEDIA_ROOT existe: {settings.MEDIA_ROOT}")
    print(f"📁 Contenu: {os.listdir(settings.MEDIA_ROOT)}")
else:
    print(f"❌ MEDIA_ROOT n'existe pas: {settings.MEDIA_ROOT}")
EOF

echo "✅ Configuration des médias terminée!"
echo "🌐 Accédez au diagnostic: /diagnostic/media/"
