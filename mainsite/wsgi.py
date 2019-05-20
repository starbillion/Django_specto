"""
WSGI config for untitled project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os
import sys


DJANGO_PATH=os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
sys.path.append(DJANGO_PATH)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mainsite.settings")

application = get_wsgi_application()
