#!/usr/bin/env python
"""
Script pour uploader les médias locaux vers S3
À exécuter en local avant de configurer Render
"""
import os
import django
import boto3
from botocore.exceptions import NoCredentialsError
from django.conf import settings

# Configuration
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_management.settings')
django.setup()

def upload_media_to_s3():
    """Upload tous les fichiers médias locaux vers S3"""
    
    print("🚀 Upload des médias vers S3...")
    
    # Vérifier la configuration S3
    if not getattr(settings, 'USE_S3', False):
        print("❌ USE_S3=False. Configurez d'abord S3 dans settings.py")
        return
    
    # Initialiser le client S3
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1')
        )
        print("✅ Client S3 initialisé")
    except NoCredentialsError:
        print("❌ Credentials S3 non trouvés")
        return
    
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    
    # Uploader les fichiers du dossier media
    media_root = settings.MEDIA_ROOT
    if not os.path.exists(media_root):
        print(f"❌ Dossier media non trouvé: {media_root}")
        return
    
    uploaded_files = []
    errors = []
    
    # Parcourir tous les fichiers dans media/
    for root, dirs, files in os.walk(media_root):
        for file in files:
            local_path = os.path.join(root, file)
            # Calculer le chemin relatif
            relative_path = os.path.relpath(local_path, media_root)
            s3_key = f"media/{relative_path}"
            
            try:
                print(f"📤 Upload: {relative_path} -> s3://{bucket_name}/{s3_key}")
                s3_client.upload_file(local_path, bucket_name, s3_key)
                uploaded_files.append(s3_key)
            except Exception as e:
                print(f"❌ Erreur upload {relative_path}: {e}")
                errors.append(f"{relative_path}: {e}")
    
    # Résumé
    print(f"\n📊 Résumé:")
    print(f"✅ Fichiers uploadés: {len(uploaded_files)}")
    print(f"❌ Erreurs: {len(errors)}")
    
    if uploaded_files:
        print(f"\n📋 Fichiers uploadés:")
        for file in uploaded_files[:10]:  # Limiter l'affichage
            print(f"  - {file}")
        if len(uploaded_files) > 10:
            print(f"  ... et {len(uploaded_files) - 10} autres")
    
    if errors:
        print(f"\n❌ Erreurs:")
        for error in errors:
            print(f"  - {error}")
    
    # Mettre à jour la base de données si nécessaire
    print(f"\n🔄 Mise à jour de la base de données...")
    try:
        from apps.menu.models import Plat
        plats = Plat.objects.exclude(image='').exclude(image__isnull=True)
        print(f"📸 {plats.count()} plats avec images trouvés")
        
        for plat in plats:
            if plat.image:
                print(f"  - {plat.nom}: {plat.image.name}")
                
    except Exception as e:
        print(f"❌ Erreur mise à jour DB: {e}")
    
    print(f"\n🎉 Upload terminé!")
    print(f"🌐 Configurez maintenant les variables d'environnement sur Render.com")

if __name__ == '__main__':
    upload_media_to_s3()
