# Guide Cloudinary - Images des Plats

## 🎯 Objectif

Remplacer S3 par Cloudinary pour un hébergement gratuit et optimisé des images des plats du restaurant.

## 🌩️ Pourquoi Cloudinary ?

### ✅ Avantages
- **Gratuit** : Plan généreux pour les petites entreprises
- **Optimisation automatique** : Images compressées et formatées
- **CDN intégré** : Rapide partout dans le monde
- **Transformations** : Redimensionnement à la volée
- **Backup** : Sauvegarde automatique
- **Simple** : Pas besoin de configurer AWS S3

### 📊 Plan gratuit Cloudinary
- 25 crédits/mois (suffisant pour un restaurant)
- Stockage illimité
- Bande passante: 25GB/mois
- Transformations: 25GB/mois

## 🚀 Installation déjà effectuée

```bash
pip install cloudinary django-cloudinary-storage
```

## ⚙️ Configuration

### 1. Variables d'environnement

Configurez ces variables dans votre dashboard d'hébergement :

```bash
# Remplacez avec vos vraies valeurs Cloudinary
CLOUDINARY_CLOUD_NAME=METTRE_ICI_VOTRE_CLOUD_NAME
CLOUDINARY_API_KEY=METTRE_ICI_VOTRE_API_KEY  
CLOUDINARY_API_SECRET=METTRE_ICI_VOTRE_API_SECRET

# Activer Cloudinary en production
USE_CLOUDINARY=true
```

### 2. Créer un compte Cloudinary

1. Allez sur [cloudinary.com](https://cloudinary.com/)
2. Créez un compte gratuit
3. Connectez-vous à votre dashboard
4. Allez dans **"Settings" > "Account" > "API Keys"**
5. Copiez les 3 valeurs requises :
   - **Cloud name** : Votre nom de cloud unique
   - **API Key** : Votre clé d'API
   - **API Secret** : Votre secret d'API (gardé confidentiel)

### 3. Configuration Django (déjà faite)

La configuration est automatique :
- **Développement** : Stockage local (`/media/`)
- **Production** : Cloudinary (si variables configurées)

## 📝 Modèle Plat (déjà configuré)

```python
class Plat(models.Model):
    nom = models.CharField(max_length=200)
    image = models.ImageField(upload_to='plats/')  # Automatiquement sur Cloudinary
    # ... autres champs
```

## 🔄 Workflow de déploiement

### 1. Configuration locale
```bash
# Test local (utilise le stockage local)
python manage.py runserver
```

### 2. Configuration production
```bash
# Dans votre dashboard (Render/Railway/Heroku)
CLOUDINARY_CLOUD_NAME=votre_cloud_name
CLOUDINARY_API_KEY=votre_api_key
CLOUDINARY_API_SECRET=votre_api_secret
USE_CLOUDINARY=true
```

### 3. Test de configuration
```bash
python test_cloudinary.py
```

## 📸 Utilisation dans l'application

### Upload d'image
```python
# Dans les vues ou formulaires
plat = Plat.objects.create(
    nom="Thieboudienne",
    image=request.FILES['image'],  # Automatiquement uploadé sur Cloudinary
    prix_unitaire=15000
)
```

### Affichage des images
```html
<!-- Dans les templates -->
<img src="{{ plat.image.url }}" alt="{{ plat.nom }}">
<!-- Génère : https://res.cloudinary.com/VOTRE_CLOUD/image/upload/v123/plats/image.jpg -->
```

## 🎨 Transformations Cloudinary

### Redimensionnement automatique
```html
<!-- Image 300x300 avec crop -->
<img src="{{ plat.image.url|crop:'300x300' }}" alt="{{ plat.nom }}">

<!-- Image avec qualité optimisée -->
<img src="{{ plat.image.url|quality:'auto' }}" alt="{{ plat.nom }}">
```

### Formats automatiques
```html
<!-- Format WebP pour les navigateurs modernes -->
<img src="{{ plat.image.url|format:'auto' }}" alt="{{ plat.nom }}">
```

## 🔍 Diagnostic et monitoring

### Logs à surveiller
```
✅ Cloudinary activé : your_cloud_name
⚠️ Stockage local activé (développement uniquement)
```

### Test de connexion
```bash
python test_cloudinary.py
```

## 🚨 Dépannage

### ❌ "Variables Cloudinary manquantes"
**Solution** : Configurez les 3 variables d'environnement requises

### ❌ "Upload échoué"
**Causes possibles** :
- Mauvaises credentials Cloudinary
- Quota dépassé (25 crédits/mois)
- Format de fichier non supporté

### ❌ "Images ne s'affichent pas"
**Vérifier** :
- URL générée par `{{ plat.image.url }}`
- Accès public au dossier Cloudinary
- Configuration CORS si nécessaire

## 📊 Migration depuis S3

### Avantages de la migration
1. **Plus simple** : Pas de configuration AWS complexe
2. **Moins cher** : Plan gratuit généreux
3. **Plus rapide** : CDN intégré
4. **Optimisé** : Compression automatique

### Étapes de migration
1. Configurer Cloudinary (ci-dessus)
2. Déployer avec variables Cloudinary
3. Les nouvelles images iront sur Cloudinary
4. (Optionnel) Migrer les anciennes images manuellement

## 🎯 Résultat final

Une fois configuré :
- ✅ Images des plats hébergées sur Cloudinary
- ✅ URLs optimisées et rapides
- ✅ Transformations d'images à la volée
- ✅ Backup automatique
- ✅ Monitoring dans dashboard Cloudinary
- ✅ Zéro configuration AWS

---

**Cloudinary est maintenant configuré et prêt à utiliser!** 🌩️🚀
