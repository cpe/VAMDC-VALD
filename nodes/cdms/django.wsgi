import os
import sys
import django

#sys.path.append('/srv/django/VAMDCNodeSoftware/')
#os.environ['DJANGO_SETTINGS_MODULE'] = 'nodes.cdms.settings'

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

#from django.core.wsgi import get_wsgi_application
#application = get_wsgi_application()

from django.core.handlers.wsgi import WSGIHandler
#django.setup(set_prefix = False)
django.setup()
application = WSGIHandler()
