#!/usr/bin/env python
"""
Script de test pour vérifier la connexion S3 avant déploiement en production
Usage: python test_s3.py
"""
import os
import sys
import boto3
from dotenv import load_dotenv

def test_s3_connection():
    """Test la connexion S3 et les permissions"""
    print("🔍 Test de connexion S3...")
    
    # Charger les variables d'environnement
    load_dotenv()
    
    # Vérifier les variables requises
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_STORAGE_BUCKET_NAME']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Variables manquantes : {', '.join(missing_vars)}")
        return False
    
    try:
        # Créer le client S3
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_S3_REGION_NAME', 'eu-west-3')
        )
        
        bucket = os.getenv('AWS_STORAGE_BUCKET_NAME')
        
        # Test 1: Vérifier si le bucket existe
        print(f"📦 Vérification du bucket : {bucket}")
        s3.head_bucket(Bucket=bucket)
        print("✅ Bucket accessible")
        
        # Test 2: Test d'upload
        print("📤 Test d'upload...")
        test_key = 'test/connexion.txt'
        s3.put_object(
            Bucket=bucket,
            Key=test_key,
            Body=b'Test de connexion S3 - Django Restaurant',
            ContentType='text/plain'
        )
        print("✅ Upload réussi")
        
        # Test 3: Test de download
        print("📥 Test de download...")
        response = s3.get_object(Bucket=bucket, Key=test_key)
        content = response['Body'].read()
        print(f"✅ Download réussi : {content.decode()}")
        
        # Test 4: Test de suppression
        print("🗑️ Test de suppression...")
        s3.delete_object(Bucket=bucket, Key=test_key)
        print("✅ Suppression réussie")
        
        # Test 5: Vérifier les permissions du bucket
        print("🔐 Vérification des permissions...")
        try:
            objects = s3.list_objects_v2(Bucket=bucket, MaxKeys=1)
            print("✅ Permissions de lecture OK")
        except Exception as e:
            print(f"⚠️ Attention : {e}")
        
        print("\n🎉 Tous les tests S3 sont passés avec succès !")
        print(f"✅ S3 prêt pour la production : {bucket}")
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR S3 : {e}")
        print("\n🔧 Solutions possibles :")
        print("1. Vérifiez vos credentials AWS")
        print("2. Vérifiez les permissions IAM de votre utilisateur")
        print("3. Vérifiez que le bucket existe et est accessible")
        print("4. Vérifiez la région S3 (eu-west-3)")
        return False

def check_environment_variables():
    """Vérifie la configuration des variables d'environnement"""
    print("\n🔍 Vérification des variables d'environnement...")
    
    env_vars = {
        'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY'),
        'AWS_STORAGE_BUCKET_NAME': os.getenv('AWS_STORAGE_BUCKET_NAME'),
        'AWS_S3_REGION_NAME': os.getenv('AWS_S3_REGION_NAME', 'eu-west-3'),
        'USE_S3': os.getenv('USE_S3', 'True'),
        'DEBUG': os.getenv('DEBUG', 'False')
    }
    
    for var, value in env_vars.items():
        if 'SECRET' in var or 'KEY' in var:
            display_value = f"{'*' * 8}{value[-4:]}" if value else "Non défini"
        else:
            display_value = value or "Non défini"
        print(f"  {var}: {display_value}")
    
    # Validation basique
    key_id = env_vars['AWS_ACCESS_KEY_ID']
    secret = env_vars['AWS_SECRET_ACCESS_KEY']
    
    if key_id and len(key_id) < 10:
        print("⚠️ AWS_ACCESS_KEY_ID semble trop court")
    if secret and len(secret) < 20:
        print("⚠️ AWS_SECRET_ACCESS_KEY semble trop court")

if __name__ == "__main__":
    print("🚀 Test de configuration S3 pour Django Restaurant\n")
    
    # Vérifier les variables
    check_environment_variables()
    
    # Tester la connexion
    success = test_s3_connection()
    
    if success:
        print("\n✅ Configuration S3 validée - prêt pour le déploiement !")
        sys.exit(0)
    else:
        print("\n❌ Configuration S3 invalide - corrigez avant déploiement")
        sys.exit(1)
