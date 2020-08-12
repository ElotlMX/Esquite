"""
Generadas por ``django-admin startproject`` usando Django ``2.2.2``.
"""

import os
import yaml
from django.contrib.messages import constants as messages

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    with open(os.path.join(BASE_DIR, "env.yaml"), 'r') as e:
        env = yaml.load(e, Loader=yaml.FullLoader)
except FileNotFoundError:
    print("[ERROR] Archivo de configuración env.yaml no encontrado")
    # Setting dummy dict for build the docs correctly at Read The Docs
    env = {"DEBUG": "False", "ORG_NAME": "", "SECRET_KEY": "dummy-key",
           "KEYBOARD": [], "COLORS": [], "L1": "", "L2": "",
           "INDEX": "test", "SOCIAL": [], "URL": "localhost", "COLABS": [],
           "NAME": "", "GOOGLE_ANALYTICS": ""}

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = eval(env['DEBUG'])
if DEBUG:
    ALLOWED_HOSTS = []
else:
    ALLOWED_HOSTS = ['*']

NAME = env['NAME']

ORG_NAME = env['ORG_NAME']

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env['SECRET_KEY']

KEYBOARD = env['KEYBOARD']

# Colores

COLORS = env['COLORS']

# Lenguas

L1 = env['L1']

L2 = env['L2']

INDEX = env["INDEX"]

# Social links

SOCIAL = env['SOCIAL']

# Colaboradoras del proyecto

COLABS = env['COLABS']

ELASTIC_URL = env["URL"]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'searcher.apps.SearcherConfig',
    'corpus_admin.apps.DocsAdminConfig',
    'google_analytics',
    'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'esquite.urls'

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
                'esquite.context_processors.user_templates',
                'esquite.context_processors.keyboard',
                'esquite.context_processors.languages',
                'esquite.context_processors.colors',
                'esquite.context_processors.project_info',
                'esquite.context_processors.google_analytics',

            ],
        },
    },
]

WSGI_APPLICATION = 'esquite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'es-mx'

TIME_ZONE = 'America/Mexico_City'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

STATIC_ROOT = BASE_DIR + '/site/assets/'

MEDIA_ROOT = '/media/'

GOOGLE_ANALYTICS = {
    'google_analytics_id': env["GOOGLE_ANALYTICS"]
}


MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}


# Logging de eventos
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}]::[{levelname}]::{name}::{message}',
            'datefmt': "%d/%b/%Y %H:%M:%S",
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}]::{message}',
            'style': '{',
        }
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/esquite.log'),
            'formatter': 'verbose'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'requests': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/tsunkua_errors.log'),
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'simple'
        }
    },
    'loggers': {
        'esquite': {
            'handlers': ['console', 'file', 'requests'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'searcher': {
            'handlers': ['console', 'file', 'requests'],
            'level': 'INFO',
            'propagate': True,
        },
        'corpus_admin': {
            'handlers': ['console', 'file', 'requests'],
            'level': 'INFO',
            'propagate': True,
        }

    },
}
