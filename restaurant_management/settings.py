import os
from pathlib import Path
from decouple import config
from dotenv import load_dotenv
load_dotenv()
try:
    import dj_database_url
except ImportError:
    dj_database_url = None

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key-change-in-production')

CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 60 * 15
CACHE_MIDDLEWARE_KEY_PREFIX = 'restaurant'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = [
    h.strip()
    for h in config(
        'ALLOWED_HOSTS',
        default='localhost,127.0.0.1,restaurant-django-production.up.railway.app,.up.railway.app',
    ).split(',') 
    if h.strip()
]

CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in config(
        'CSRF_TRUSTED_ORIGINS',
        default='https://restaurant-django-production.up.railway.app,https://*.up.railway.app',
    ).split(',')
    if o.strip()
]

# Application definition
INSTALLED_APPS = [
    'sslserver',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    # Apps locales
    'apps.authentication',
    'apps.tables',
    'apps.menu',
    'apps.orders',
    'apps.payments',
    'apps.expenses',
    'apps.core',
    'apps.dashboard',
    'storages',
   
]

# Configuration S3
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', 'mon-restaurant-media-2026')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
# Remove ACL settings as they're not supported by the bucket
AWS_QUERYSTRING_AUTH = False
AWS_S3_REGION_NAME = 'eu-west-3'
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_LOCATION = 'media'
# Disable ACLs and use bucket policy for access control
AWS_DEFAULT_ACL = None
AWS_S3_FILE_OVERWRITE = False

# Stockage des médias
USE_S3 = config('USE_S3', default=False, cast=bool)
HAS_S3_CREDS = bool(AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_STORAGE_BUCKET_NAME)

if USE_S3 and HAS_S3_CREDS:
    DEFAULT_FILE_STORAGE = 'restaurant_management.storage_backend.MediaStorage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'
else:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    MEDIA_ROOT = BASE_DIR / 'media'
    MEDIA_URL = '/media/'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

if not DEBUG:
    try:
        import django_redis  # noqa: F401
        CACHES['default'] = {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': 'redis://127.0.0.1:6379/1',
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'SOCKET_CONNECT_TIMEOUT': 5,
                'SOCKET_TIMEOUT': 5,
                'IGNORE_EXCEPTIONS': True,
                'KEY_PREFIX': 'restaurant',
            }
        }
    except ImportError:
        pass

# Configuration pour la production
if not DEBUG:
    # Sécurité en production
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Configuration de la base de données MySQL
# Configuration de la base de données
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('MYSQLDATABASE', 'railway'),
        'USER': os.getenv('MYSQLUSER', 'root'),
        'PASSWORD': os.getenv('MYSQLPASSWORD', 'qfwbhaOFfumhinTZCSpAYyDpccXUcgJL'),
        'HOST': os.getenv('MYSQLHOST', 'metro.proxy.rlwy.net'),
        'PORT': os.getenv('MYSQLPORT', '44250'),  # Laissez en tant que chaîne
        'OPTIONS': {
            'charset': 'utf8mb4',
            'ssl': {'ssl': {}}
        }
    }
}

# Configuration alternative avec dj_database_url
if os.environ.get('DATABASE_URL'):
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=False,
        conn_max_identity_ltree=100  # Ajout de cette option
    )



# Configuration pour la base de données de production via DATABASE_URL (prioritaire)
DATABASE_URL = os.environ.get('DATABASE_URL') or config('DATABASE_URL', default='')
if DATABASE_URL:
    if dj_database_url is None:
        raise RuntimeError('DATABASE_URL is set but dj_database_url is not installed. Install dj-database-url.')
    DATABASES['default'] = dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        ssl_require=False,
    )
    DATABASES['default'].setdefault('OPTIONS', {})
    DATABASES['default']['OPTIONS'].pop('sslmode', None)

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies' if DEBUG else 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 86400
SESSION_SAVE_EVERY_REQUEST = False

# URLs et modèles
ROOT_URLCONF = 'restaurant_management.urls'
WSGI_APPLICATION = 'restaurant_management.wsgi.application'
AUTH_USER_MODEL = 'authentication.CustomUser'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Internationalization
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Configuration des templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries': {
                'staticfiles': 'django.templatetags.static',
            }
        },
    },
]

# Configuration des fichiers statiques et médias
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Configuration de WhiteNoise pour servir les fichiers statiques
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.authentication.middleware.RoleBasedAccessMiddleware',
]

if not DEBUG:
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
        'django.middleware.cache.UpdateCacheMiddleware',
    ] + MIDDLEWARE[1:] + [
        'django.middleware.cache.FetchFromCacheMiddleware',
    ]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_MAX_AGE = 31536000
WHITENOISE_USE_FINDERS = True

# Configuration pour la compression des fichiers statiques
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = not DEBUG

# Configuration des médias

# Configuration des validateurs de mot de passe
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'apps.authentication.validators.CustomPasswordValidator',
    },
]

LOGIN_URL = 'authentication:login'
LOGIN_REDIRECT_URL = 'authentication:redirect_after_login'
LOGOUT_REDIRECT_URL = 'authentication:login'

CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

CRONJOBS = [
    ('0 0 * * *', 'apps.dashboard.cron.send_daily_cash_report'),
]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@restaurant.com')
