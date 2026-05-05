import os
import sys

# Put the backend root on the path so Django can find sibaha_backend/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sibaha_backend.settings")

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()

# Vercel's Python runtime looks for a variable named 'handler' or 'app'
handler = application
