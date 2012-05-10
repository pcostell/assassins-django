import os
import sys

sys.path.insert(0, '') # Put path to project here.

os.environ['DJANGO_SETTINGS_MODULE'] = 'assassins_project.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

