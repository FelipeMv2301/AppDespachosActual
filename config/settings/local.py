from .base import *
from .base import ALLOWED_PRIVATE_HOSTS, ALLOWED_PUBLIC_HOSTS, env

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env.str(
    var='SECRET_KEY',
    default='oFSZeObw6MzbdYflLy9wn3Ywwol7rOpZpwxEAP8Jz9Vch0HsSDuvSF9IKoeQrzsV',
)

# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ALLOWED_PUBLIC_HOSTS + ALLOWED_PRIVATE_HOSTS
CSRF_TRUSTED_ORIGINS = env.list(
    var='CSRF_TRUSTED_ORIGINS',
    default=['localhost', '0.0.0.0', '127.0.0.1']
)

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-age
SESSION_COOKIE_AGE = env.int(var='SESSION_COOKIE_AGE')


# DJANGO DEBUG TOOLBAR
# ------------------------------------------------------------------------------
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#prerequisites
DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': ['debug_toolbar.panels.redirects.RedirectsPanel'],
    'SHOW_TEMPLATE_CONTEXT': True,
}
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#internal-ips
INTERNAL_IPS = env.list(var='INTERNAL_IPS',
                        default=['127.0.0.1'])
