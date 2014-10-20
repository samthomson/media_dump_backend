import os
import sys	

sys.path.insert(0, '/var/www/media_dump_app')

sys.path.append('~/var/www/mdaclient/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'media_dump.settings'
#import django.core.handlers.wsgi
#application = django.core.handlers.wsgi.WSGIHandler()
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()