#!/usr/bin/env python
import os
import sys
import django

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_management.settings')
django.setup()

def test_simple_media():
    """Test simple et direct des médias"""
    print("🧪 Test simple des médias...")
    
    from django.conf import settings
    from django.test import Client
    
    # Configuration
    print(f"DEBUG: {settings.DEBUG}")
    print(f"USE_S3: {getattr(settings, 'USE_S3', False)}")
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"MEDIA_URL: {settings.MEDIA_URL}")
    
    # Créer un fichier de test
    test_file = os.path.join(settings.MEDIA_ROOT, 'test_simple.txt')
    with open(test_file, 'w') as f:
        f.write("Test content - simple verification")
    
    print(f"✅ Fichier de test créé: {test_file}")
    
    # Test avec le client Django
    client = Client()
    
    # Simuler DEBUG=False pour tester la production
    original_debug = settings.DEBUG
    settings.DEBUG = False
    
    try:
        response = client.get('/media/test_simple.txt')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            # Pour FileResponse, utiliser streaming_content
            if hasattr(response, 'streaming_content'):
                content = b''.join(response.streaming_content).decode()
            else:
                content = response.content.decode()
            print(f"Content: {content}")
            print("✅ Médias fonctionnent en production !")
        else:
            print(f"❌ Erreur: {response.status_code}")
            if hasattr(response, 'content'):
                print(f"Response: {response.content.decode()}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    finally:
        # Restaurer DEBUG
        settings.DEBUG = original_debug
    
    print("\n🔍 Test avec DEBUG=True (développement):")
    try:
        response = client.get('/media/test_simple.txt')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Médias fonctionnent en développement !")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == '__main__':
    test_simple_media()
