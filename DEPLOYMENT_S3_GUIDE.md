# Guide de Déploiement S3 - Médias des Plats

## 🎯 Problème identifié

En local, les images des plats fonctionnent bien avec le stockage local, mais en production elles ne s'affichent pas à cause d'une configuration S3 incorrecte.

## 🔧 Solution appliquée

La configuration a été entièrement refaite pour utiliser **STORAGES** (Django 4.2+) au lieu de l'ancien `DEFAULT_FILE_STORAGE`.

## 📋 Variables d'environnement requises

Configurez ces variables dans votre dashboard d'hébergement (Render/Railway/Heroku):

### 🔐 Credentials AWS
```bash
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_STORAGE_BUCKET_NAME=mon-restaurant-media-2026
AWS_S3_REGION_NAME=eu-west-3
```

### 🚀 Configuration Production
```bash
USE_S3=true
DEBUG=false
```

## 🗂️ Structure S3 recommandée

```
mon-restaurant-media-2026/
├── media/
│   ├── plats/
│   │   ├── image_plat_1.jpg
│   │   ├── image_plat_2.png
│   │   └── ...
│   └── autres_fichiers/
└── static/ (géré par collectstatic)
```

## 🔍 Vérification avant déploiement

### 1. Test de connexion S3
```bash
python test_s3.py
```

### 2. Test configuration médias
```bash
python test_media_config.py
```

### 3. System check Django
```bash
python manage.py check --deploy
```

## 🚨 Erreurs communes et solutions

### ❌ "DEFAULT_FILE_STORAGE/STORAGES are mutually exclusive"
**Solution**: La configuration utilise maintenant `STORAGES` uniquement.

### ❌ "STATICFILES_STORAGE/STORAGES are mutually exclusive"  
**Solution**: `STATICFILES_STORAGE` a été supprimé, utilise `STORAGES['staticfiles']`.

### ❌ Images ne s'affichent pas en production
**Causes possibles**:
1. Variables S3 manquantes
2. Bucket S3 non public
3. Permissions IAM incorrectes
4. CORS non configuré

## 🔐 Permissions IAM requises

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::mon-restaurant-media-2026",
                "arn:aws:s3:::mon-restaurant-media-2026/*"
            ]
        }
    ]
}
```

## 🌐 Policy S3 (Bucket Public)

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::mon-restaurant-media-2026/*"
        }
    ]
}
```

## 🔄 Workflow de déploiement

1. **Configurer les variables** d'environnement S3
2. **Tester la connexion** avec `test_s3.py`
3. **Vérifier la configuration** avec `test_media_config.py`
4. **Déployer** sur votre plateforme
5. **Vérifier les logs** pour les messages S3

## 📊 Monitoring en production

### Logs à surveiller:
- `✅ S3 activé : mon-restaurant-media-2026 (eu-west-3)`
- `⚠️ Stockage local activé (développement uniquement)`

### Fichier de log:
- `django_s3_errors.log` (erreurs S3)

## 🎯 Résultat attendu

Une fois configuré correctement:
- ✅ Images des plats visibles en production
- ✅ Uploads fonctionnels
- ✅ URLs S3 générées automatiquement
- ✅ Fallback local en développement

## 🆘 Support

Si vous rencontrez encore des problèmes:
1. Vérifiez les variables d'environnement
2. Testez avec `python diagnose_s3.py`
3. Consultez les logs d'erreur S3
4. Vérifiez les permissions AWS IAM

---

**La configuration est maintenant prête pour la production!** 🚀
