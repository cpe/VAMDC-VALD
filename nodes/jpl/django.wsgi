import os
import sys
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

#from django.core.wsgi import get_wsgi_application
#application = get_wsgi_application()

from django.core.handlers.wsgi import WSGIHandler
#django.setup(set_prefix = False)
django.setup()
application = WSGIHandler()
