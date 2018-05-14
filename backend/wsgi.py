"""
WSGI config for backend project.

This exposes the WSGI callable as a module-level variable named "application".

This can also call one-time startup code.
"""
import os

from dj_static import Cling
from django.core.wsgi import get_wsgi_application

# The code below is what actually starts the server.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

application = Cling(get_wsgi_application())
