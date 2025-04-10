from pathlib import Path
from os import path

# django-environ
# https://django-environ.readthedocs.io/en/latest/
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

env = environ.Env()
env.read_env(path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', False)

ALLOWED_HOSTS = env('ALLOWED_HOSTS', list, [])

INTERNAL_IPS = ALLOWED_HOSTS

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    #'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'debug_toolbar',
    'sorl.thumbnail',
    'portfolio',
]

MIDDLEWARE = [
    #'django.middleware.cache.UpdateCacheMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

   # 'django.middleware.cache.FetchFromCacheMiddleware',
    #'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# CACHE_MIDDLEWARE_SECONDS = 60*5
# CACHE_MIDDLEWARE_KEY_PREFIX = ''
# CACHE_MIDDLEWARE_ALIAS = 'default'

ROOT_URLCONF = 'crm.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'crm.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases


DATABASES = {
    'default': env.db()
}


CACHES = {
    'default': env.cache()
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


FILE_UPLOAD_HANDLERS = [
    "portfolio.logic.ImageUploadHandler",
    "django.core.files.uploadhandler.MemoryFileUploadHandler",
    "django.core.files.uploadhandler.TemporaryFileUploadHandler"
 ]

FILE_UPLOAD_MAX_MEMORY_SIZE = 5*1024*1024
MAX_UPLOAD_FILES_SIZE = 20*FILE_UPLOAD_MAX_MEMORY_SIZE

THUMBNAIL_QUALITY = 80
THUMBNAIL_UPSCALE = False
THUMBNAIL_FILTER_WIDTH = 600

ADMIN_THUMBNAIL_QUALITY = 75
ADMIN_THUMBNAIL_SIZE = [100, 100]

DJANGORESIZED_DEFAULT_QUALITY = 85
DJANGORESIZED_DEFAULT_SIZE = [1500, 1024]
DJANGORESIZED_DEFAULT_KEEP_META = False

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

PUBLIC_ROOT = ''

STATIC_URL = '/static/'

if not DEBUG:
    STATIC_ROOT = path.join(BASE_DIR, PUBLIC_ROOT + 'static/')
    STATICFILES_DIRS = [
        path.join(BASE_DIR, PUBLIC_ROOT + 'assets/'),
    ]
else:
    #STATIC_ROOT = ''
    STATICFILES_DIRS = [
        path.join(BASE_DIR, PUBLIC_ROOT + 'static/'),
    ]

# Base url to serve media files
MEDIA_URL = '/media/'

MEDIA_ROOT = path.join(BASE_DIR, PUBLIC_ROOT + 'media/')

FILES_UPLOAD_FOLDER = 'uploads/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
