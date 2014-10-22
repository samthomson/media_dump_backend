activate_this = '/home/sam/.virtualenvs/media_dump_env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))


import os





import sys	

path = '/var/www/media_dump'
if path not in sys.path:
    sys.path.append(path)


sys.path.insert(0, '/var/www/media_dump_app')

sys.path.append('~/var/www/mdaclient/')



os.environ['DJANGO_SETTINGS_MODULE'] = 'media_dump.settings'
#import django.core.handlers.wsgi
#application = django.core.handlers.wsgi.WSGIHandler()
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()