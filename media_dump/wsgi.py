import os
import sys	
sys.path.append('~/var/www/mdaclient/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'media_dump.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()