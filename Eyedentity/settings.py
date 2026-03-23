from pathlib import Path
from django.contrib.messages import constants as messages
import dj_database_url
import os

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / '.env')
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.onrender.com',
    '.fly.dev',
    'eyedentity.co.zw',
    'www.eyedentity.co.zw',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'ckeditor',
    'ckeditor_uploader',
    'crispy_forms',
    'crispy_bootstrap5',
    'storages',
    'apps.main',
    'apps.blog',
]

if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG:
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

ROOT_URLCONF = 'Eyedentity.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.main.views.site_context',
                'apps.main.views.wishlist_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'Eyedentity.wsgi.application'

DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=not DEBUG,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'eyedentity'),
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD', 'admin123'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Harare'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_ROOT = BASE_DIR / 'media'

SUPABASE_PROJECT_ID = 'jmzrevalerojybgvxfas'
AWS_STORAGE_BUCKET_NAME = 'media'
AWS_ACCESS_KEY_ID = os.environ.get('SUPABASE_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('SUPABASE_SECRET_ACCESS_KEY')
AWS_S3_ENDPOINT_URL = f'https://{SUPABASE_PROJECT_ID}.supabase.co/storage/v1/s3'
AWS_S3_REGION_NAME = 'us-east-1'
AWS_S3_ADDRESSING_STYLE = 'path'
AWS_QUERYSTRING_AUTH = False
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_SIGNATURE_VERSION = 's3v4'

MEDIA_URL = f'https://{SUPABASE_PROJECT_ID}.supabase.co/storage/v1/object/public/{AWS_STORAGE_BUCKET_NAME}/'

if DEBUG:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }
else:
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {
                "bucket_name": "media",
                "endpoint_url": f'https://{SUPABASE_PROJECT_ID}.supabase.co/storage/v1/s3',
                "region_name": "us-east-1",
                "addressing_style": "path",
                "signature_version": "s3v4",
                "querystring_auth": False,
                "file_overwrite": False,
                "default_acl": "public-read",
                "custom_domain": f'{SUPABASE_PROJECT_ID}.supabase.co/storage/v1/object/public/media',
            },
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SITE_ID = 1

SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_JQUERY_URL = 'https://ajax.googleapis.com/ajax/libs/jquery/2.2.4/jquery.min.js'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
        'extraPlugins': ','.join([
            'uploadimage', 'div', 'autolink', 'autoembed',
            'embedsemantic', 'autogrow', 'widget', 'lineutils',
            'clipboard', 'dialog', 'dialogui', 'elementspath',
        ]),
        'removePlugins': ','.join(['stylesheetparser']),
    },
    'awesome_ckeditor': {
        'toolbar': 'Basic',
    },
}

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

SESSION_COOKIE_AGE = 1209600
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = False

MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

PAGINATE_BY = 12
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880
THUMBNAIL_SIZE = (300, 300)
PRODUCT_IMAGE_SIZE = (800, 600)
BLOG_IMAGE_SIZE = (1200, 600)

DEFAULT_META_DESCRIPTION = "Eyedentity Eyewear - Premium eyewear solutions in Harare, Zimbabwe. Stylish, protective, and uniquely you."
DEFAULT_META_KEYWORDS = "eyewear, glasses, sunglasses, Harare, Zimbabwe, blue light, photochromic, polarized"

if DEBUG:
    INTERNAL_IPS = ['127.0.0.1', 'localhost']