#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings
from django.test import Client
from django.urls import reverse
from django.core.management import execute_from_command_line

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_management.settings')
django.setup()

def test_media_configuration():
    """Test complet de la configuration des médias"""
    print("🔍 Test de la configuration des médias en production...")
    print("=" * 50)
    
    # 1. Vérifier la configuration Django
    print("\n📋 Configuration Django:")
    print(f"  DEBUG: {settings.DEBUG}")
    print(f"  USE_S3: {getattr(settings, 'USE_S3', False)}")
    print(f"  MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"  MEDIA_URL: {settings.MEDIA_URL}")
    print(f"  WHITENOISE_ROOT: {getattr(settings, 'WHITENOISE_ROOT', 'Non défini')}")
    
    # 2. Vérifier les dossiers
    print("\n📁 Vérification des dossiers:")
    if settings.MEDIA_ROOT:
        media_exists = os.path.exists(settings.MEDIA_ROOT)
        print(f"  MEDIA_ROOT existe: {'✅' if media_exists else '❌'}")
        
        if media_exists:
            media_readable = os.access(settings.MEDIA_ROOT, os.R_OK)
            print(f"  MEDIA_ROOT lisible: {'✅' if media_readable else '❌'}")
            
            # Lister les sous-dossiers
            subdirs = []
            for item in os.listdir(settings.MEDIA_ROOT):
                item_path = os.path.join(settings.MEDIA_ROOT, item)
                if os.path.isdir(item_path):
                    subdirs.append(item)
            print(f"  Sous-dossiers: {subdirs}")
            
            # Vérifier media/plats
            plats_dir = os.path.join(settings.MEDIA_ROOT, 'plats')
            if os.path.exists(plats_dir):
                plats_files = os.listdir(plats_dir)[:5]  # Limiter à 5 fichiers
                print(f"  Fichiers dans media/plats: {plats_files}")
            else:
                print("  ⚠️  Dossier media/plats n'existe pas")
    
    # 3. Tester les URLs des images
    print("\n🖼️  Test des URLs d'images:")
    try:
        from apps.menu.models import Plat
        plats_with_images = Plat.objects.exclude(image='').exclude(image__isnull=True)[:3]
        
        client = Client()
        
        for plat in plats_with_images:
            if plat.image:
                image_url = plat.image.url
                print(f"  Plat: {plat.nom}")
                print(f"    Path: {plat.image.name}")
                print(f"    URL: {image_url}")
                
                # Tester l'URL
                try:
                    response = client.get(image_url)
                    status = '✅' if response.status_code == 200 else '❌'
                    print(f"    Status: {status} ({response.status_code})")
                    
                    if response.status_code == 200:
                        content_type = response.get('Content-Type', 'Unknown')
                        print(f"    Content-Type: {content_type}")
                except Exception as e:
                    print(f"    Erreur: ❌ {e}")
                print()
    
    except Exception as e:
        print(f"  Erreur lors du test des images: {e}")
    
    # 4. Tester le middleware
    print("\n🔧 Test du middleware personnalisé:")
    try:
        from restaurant_management.middleware import MediaMiddleware
        print("  ✅ Middleware MediaMiddleware importé avec succès")
        
        # Créer une requête factice
        from django.http import HttpRequest
        request = HttpRequest()
        request.path = '/media/test.jpg'
        
        middleware = MediaMiddleware(lambda r: None)
        print("  ✅ Middleware instancié avec succès")
        
    except Exception as e:
        print(f"  ❌ Erreur middleware: {e}")
    
    # 5. Recommandations
    print("\n💡 Recommandations:")
    
    if not settings.MEDIA_ROOT or not os.path.exists(settings.MEDIA_ROOT):
        print("  ❌ Créez le dossier MEDIA_ROOT:")
        print(f"     mkdir -p {settings.MEDIA_ROOT}")
        print(f"     mkdir -p {settings.MEDIA_ROOT}/plats")
    
    if settings.DEBUG:
        print("  ℹ️  Passez DEBUG=False pour tester la configuration production")
    
    if getattr(settings, 'USE_S3', False):
        print("  ℹ️  S3 est activé - les médias seront servis depuis S3")
    else:
        print("  ✅ Configuration locale - les médias seront servis par le middleware")
    
    print("\n🚀 Pour tester en production:")
    print("  1. Définissez DEBUG=False dans .env")
    print("  2. Redémarrez le serveur")
    print("  3. Accédez à /diagnostic/media/")
    
    print("\n" + "=" * 50)
    print("✅ Test terminé!")

if __name__ == '__main__':
    test_media_configuration()
