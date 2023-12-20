import logging
import logging.config
import os
import sys
from pathlib import Path

import environ
from bitmath import MB

RUNNING_MIGRATIONS = 'migrate' in sys.argv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CURRENT_DIR = Path(__file__).resolve().parent

env_filepath = os.path.join(BASE_DIR, '.env')
env = environ.Env()
environ.Env.read_env(env_file=env_filepath)

# SETTINGS MODULE
# ---------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/4.2/topics/settings/#designating-the-settings
SETTINGS_MODULE = env.str(var='SETTINGS_MODULE')
PROJECT_NAME = SETTINGS_MODULE.split(sep='.')[0]
APP_USERNAME = 'django'

# HOSTS
# ---------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_PUBLIC_HOSTS = env.list(var='ALLOWED_PUBLIC_HOSTS')
ALLOWED_PRIVATE_HOSTS = env.list(var='ALLOWED_PRIVATE_HOSTS')

# STATIC
# ------------------------------------------------------------------------------

# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool(var='DEBUG_MODE', default=False)

if DEBUG:
    # https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
else:
    # https://docs.djangoproject.com/en/dev/ref/settings/#static-root
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# MEDIA
# ------------------------------------------------------------------------------

# https://docs.djangoproject.com/en/4.2/ref/settings/#media-url
MEDIA_URL = '/media/'
# https://docs.djangoproject.com/en/4.2/ref/settings/#std-setting-MEDIA_ROOT
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
if not os.path.exists(path=MEDIA_ROOT):
    os.mkdir(path=MEDIA_ROOT)

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/
LANGUAGE_CODE = env.str(var='LANGUAGE_CODE')
TIME_ZONE = env.str(var='TIME_ZONE')
USE_I18N = env.bool(var='USE_I18N')
USE_TZ = env.bool(var='USE_TIME_ZONE')


# DATABASES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': env.str(var='DB_ENGINE',
                          default='django.db.backends.sqlite3'),
        'NAME': env.str(var='DB_NAME',
                        default=os.path.join(BASE_DIR, 'db.sqlite3')),
        'USER': env.str(var='DB_USER', default=''),
        'PASSWORD': env.str(var='DB_PASSWORD', default=''),
        'HOST': env.str(var='DB_HOST', default=''),
        'PORT': env.int(var='DB_PORT', default=0),
    }
}
# https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-DEFAULT_AUTO_FIELD
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
if RUNNING_MIGRATIONS:
    ROOT_URLCONF = ''
else:
    ROOT_URLCONF = 'project.urls'

LOGIN_URL = '/'

# WSGI
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'project.wsgi.application'

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap5',
    'debug_toolbar',
    'django_extensions',
    'simple_history',
    'rest_framework',
]
THIRD_PARTY_APPS = []

LOCAL_APPS = [
    'api',
    'module.authentication',
    'module.business_partner',
    'module.delivery',
    'module.general',
    'module.order',
]
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# DJANGO SHELL PLUS
# ------------------------------------------------------------------------------
# https://django-extensions.readthedocs.io/en/latest/shell_plus.html
SHELL_PLUS = 'python'


# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = [
    # https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
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

# SESSION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/4.2/topics/http/sessions/#using-cookie-based-sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),
                 os.path.join(BASE_DIR, 'notification', 'templates')],
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

# Settings for django-bootstrap-v5
BOOTSTRAP5 = {
    'error_css_class': 'bootstrap5-error',
    'required_css_class': 'bootstrap5-required',
    'javascript_in_head': True,
}


# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env.str(var='EMAIL_BACKEND')
EMAIL_HOST = env.str(var='EMAIL_HOST')
EMAIL_PORT = env.int(var='EMAIL_PORT')
EMAIL_USE_TLS = env.bool(var='EMAIL_TLS', default=True)
EMAIL_HOST_USER = env.str(var='EMAIL_USER')
EMAIL_HOST_PASSWORD = env.str(var='EMAIL_PASSWORD')
# https://docs.djangoproject.com/en/dev/ref/settings/#email-timeout
EMAIL_TIMEOUT = env.int(var='EMAIL_TIMEOUT')

# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/4.1/topics/logging/
LOG_DIR = os.path.join(BASE_DIR, 'log')
LOG_FILENAME = 'app.log'
LOG_FILEPATH = os.path.join(LOG_DIR, LOG_FILENAME)
os.makedirs(name=LOG_DIR, exist_ok=True)

LOGLEVEL = env.str(var='LOGLEVEL', default='info').upper()
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': LOGLEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': LOGLEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILEPATH,
            'encoding': 'utf-8',
            'formatter': 'verbose',
            'maxBytes': int(MB(value=10).bytes),
            'backupCount': 5,
        },
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} [{asctime:s}] {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'loggers': {
        '': {
            'handlers': ['file', 'console'],
            'level': LOGLEVEL,
            'propagate': True,
        },
        'django': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}
if 'test' in sys.argv:
    LOGGING['loggers']['']['handlers'] = ['console']

# Global logger configuration
logging.config.dictConfig(LOGGING)
logger = logging.getLogger('')
