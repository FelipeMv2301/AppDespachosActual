from .base import *
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool(var='DEBUG_MODE')
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env.str(var='SECRET_KEY')
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list(var='ALLOWED_HOSTS')
CSRF_TRUSTED_ORIGINS = env.list(var='CSRF_TRUSTED_ORIGINS')
INTERNAL_IPS = env.list(var='INTERNAL_IPS')

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-secure
# SESSION_COOKIE_SECURE = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-secure
# CSRF_COOKIE_SECURE = True
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-age
SESSION_COOKIE_AGE = env.int(var='SESSION_COOKIE_AGE')
