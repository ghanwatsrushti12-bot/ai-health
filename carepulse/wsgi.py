"""WSGI config for the CarePulse project."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carepulse.settings.production")

application = get_wsgi_application()
