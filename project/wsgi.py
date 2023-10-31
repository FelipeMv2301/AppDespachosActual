"""
WSGI config.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from project.settings.base import SETTINGS_MODULE

os.environ.setdefault(key='DJANGO_SETTINGS_MODULE', value=SETTINGS_MODULE)

application = get_wsgi_application()
