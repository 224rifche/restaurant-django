# Restaurant Management (Django)

## Déploiement en ligne (Render + PostgreSQL)

Ce guide explique comment déployer ce projet Django sur **Render** avec une base de données **PostgreSQL**.

---

## 1) Pré-requis

- Un compte **GitHub** (le projet doit être push sur un repo)
- Un compte **Render**
- Python (géré par Render)

---

## 2) Créer la base PostgreSQL (Render)

1. Sur Render: **New** -> **PostgreSQL**
2. Donne un nom (ex: `restaurant-db`)
3. Crée la base
4. Récupère la variable `DATABASE_URL` (Render peut aussi l’injecter automatiquement si tu lies la DB au service web)

---

## 3) Créer le service Web (Render)

1. Sur Render: **New** -> **Web Service**
2. Connecte ton repo GitHub
3. Choisis la branche (ex: `main`)

### Build Command (Render)
Utilise ce build command:

```
python -m pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
```

### Start Command (Render)

```
gunicorn restaurant_management.wsgi:application
```

Note: `gunicorn` ne fonctionne pas sur Windows (erreur `No module named 'fcntl'`). C'est normal. Sur Render (Linux), `gunicorn` fonctionne.

---

## 4) Variables d’environnement (Render)

Dans Render -> Settings -> Environment, ajoute:

- `DEBUG` = `False`
- `SECRET_KEY` = une valeur forte (ex: générée aléatoirement)
- `ALLOWED_HOSTS` = `ton-service.onrender.com`
- `CSRF_TRUSTED_ORIGINS` = `https://ton-service.onrender.com`
- `DATABASE_URL` = (valeur fournie par Render PostgreSQL)

Optionnel (si email activé):

- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `DEFAULT_FROM_EMAIL`

---

## 5) Créer un admin (superuser)

Après le premier déploiement, ouvre une **Shell** sur Render (ou exécute une commande “Run” si disponible) et lance:

```
python manage.py createsuperuser
```

Ensuite connecte-toi à:

- `/admin/`

---

## 6) Notes importantes

- En production (`DEBUG=False`), les fichiers statiques sont servis via **WhiteNoise** (déjà configuré dans `restaurant_management/settings.py`).
- Le projet utilise `DATABASE_URL` quand elle est définie (PostgreSQL en prod), sinon SQLite en local.

---

## Lancement en local (développement)

1. Crée un environnement virtuel
2. Installe les dépendances:

```
python -m pip install -r requirements.txt
```

3. Lance les migrations:

```
python manage.py migrate
```

4. Démarre le serveur:

```
python manage.py runserver
```

Sur Windows, n'essaie pas de lancer `gunicorn` localement. Utilise `runserver`.

---

## Accès (exemples)

- Login: `/login/`
- Tables: `/tables/`
- Commandes: `/orders/`
- Admin: `/admin/`
