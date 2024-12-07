import os
import sys

path = '/home/TedisRozenfelds/django-apps/django/'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'django_apps.settings'

# then:
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
