# 🖼️ Résolution des problèmes de médias en production

## 📋 Problème
Les images ne s'affichent pas en production (`DEBUG=False`)

## 🔧 Solution complète implémentée

### 1. Middleware personnalisé
Un middleware `MediaMiddleware` a été créé pour servir les fichiers médias en production quand S3 n'est pas utilisé.

**Fichier**: `restaurant_management/middleware.py`
- Intercepte les requêtes `/media/*`
- Vérifie la sécurité des chemins
- Sert les fichiers avec les bons headers HTTP
- Ajoute le cache pour optimiser les performances

### 2. Configuration Django
La configuration a été simplifiée et optimisée:

**Dans `settings.py`**:
```python
if not DEBUG:
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
        'restaurant_management.middleware.MediaMiddleware',  # Notre middleware
        # ...
    ]
    
    if not USE_S3:
        WHITENOISE_ROOT = os.path.join(BASE_DIR, 'media')
        WHITENOISE_SKIP_REGULAR_MIME_TYPES = True
        WHITENOISE_INDEX_FILE = True
```

### 3. Outils de diagnostic

#### Vue de diagnostic
- **URL**: `/diagnostic/media/`
- **Fonction**: Vérifie toute la configuration des médias
- **Affiche**: Configuration Django, état des dossiers, test des URLs

#### Script de test
- **Fichier**: `test_media.py`
- **Usage**: `python test_media.py`
- **Fonction**: Test complet de la configuration

#### Script de configuration
- **Fichier**: `setup_media.bat` (Windows)
- **Usage**: Double-cliquer ou exécuter
- **Fonction**: Configure automatiquement les médias

## 🚀 Comment déployer

### Étape 1: Configuration automatique
```bash
# Windows
setup_media.bat

# Linux/Mac
chmod +x setup_media.sh
./setup_media.sh
```

### Étape 2: Configuration production
Dans votre fichier `.env`:
```env
DEBUG=False
USE_S3=False
```

### Étape 3: Redémarrer le serveur
```bash
# Redémarrez votre serveur web (Gunicorn, uWSGI, etc.)
```

### Étape 4: Vérifier
1. Accédez à: `http://votre-domaine.com/diagnostic/media/`
2. Vérifiez que tous les badges sont verts ✅
3. Testez: `http://votre-domaine.com/media/test.txt`

## 🔍 Débogage

### Si les images ne s'affichent toujours pas:

#### 1. Vérifier la configuration
```bash
python test_media.py
```

#### 2. Vérifier les logs du serveur
Cherchez les erreurs 404 pour les URLs `/media/*`

#### 3. Vérifier les permissions
```bash
# Vérifier que le dossier media est lisible
ls -la media/
```

#### 4. Tester manuellement
```bash
# Créer un fichier de test
echo "test" > media/test.txt
# Tester l'URL
curl http://votre-domaine.com/media/test.txt
```

## 📋 Checklist de déploiement

- [ ] Exécuter `setup_media.bat`
- [ ] Définir `DEBUG=False` dans `.env`
- [ ] Définir `USE_S3=False` dans `.env`
- [ ] Redémarrer le serveur
- [ ] Accéder à `/diagnostic/media/`
- [ ] Tester une URL d'image existante
- [ ] Vérifier les logs d'erreurs

## 🎯 Ce qui est maintenant configuré

### En production (`DEBUG=False`, `USE_S3=False`):
1. **WhiteNoise** sert les fichiers statiques
2. **MediaMiddleware** sert les fichiers médias
3. **Cache** configuré pour 1 an
4. **Sécurité** contre les attaques de path traversal
5. **Types MIME** corrects pour les images

### Sécurité:
- ✅ Protection contre `../` dans les URLs
- ✅ Vérification que les fichiers sont bien dans `MEDIA_ROOT`
- ✅ Types MIME validés
- ✅ Headers de cache appropriés

## 🆘 Si ça ne fonctionne toujours pas

### Options alternatives:

#### Option 1: Configuration manuelle dans urls.py
```python
# Ajouter à la fin de urls.py
if not settings.DEBUG and not getattr(settings, 'USE_S3', False):
    from django.views.static import serve
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
```

#### Option 2: Configuration Nginx/Apache
Si vous utilisez Nginx:
```nginx
location /media/ {
    alias /path/to/your/project/media/;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

#### Option 3: Utiliser S3
Configurer S3 pour stocker les médias:
```env
USE_S3=True
AWS_ACCESS_KEY_ID=votre_key
AWS_SECRET_ACCESS_KEY=votre_secret
AWS_STORAGE_BUCKET_NAME=votre_bucket
```

## 📞 Support

Si le problème persiste:
1. Exécutez `python test_media.py` et partagez le résultat
2. Accédez à `/diagnostic/media/` et partagez une capture d'écran
3. Vérifiez les logs du serveur pour les erreurs 404/500

---

**✅ Avec cette configuration, les images devraient fonctionner parfaitement en production !**
