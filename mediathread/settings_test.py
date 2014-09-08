# flake8: noqa
from settings_shared import *
import os

DEBUG = True

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_PATH, '../lettuce.db'),
        'OPTIONS': {
            'timeout': 30,
        }
    }
}

LETTUCE_SERVER_PORT = 8002
#BROWSER = 'Firefox'
BROWSER = 'Headless'
#BROWSER = 'Chrome'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LETTUCE_APPS = (
    'mediathread.main',
    'mediathread.projects',
    'mediathread.assetmgr',
    'mediathread.djangosherd'
)

#ACCOUNT_AUTHENTICATION_METHOD = "username_email"
#ACCOUNT_EMAIL_VERIFICATION = "optional"


LETTUCE_DJANGO_APP = ['lettuce.django']
INSTALLED_APPS = INSTALLED_APPS + LETTUCE_DJANGO_APP

COMPRESS_ROOT = "/Users/sdreher/workspace/mediathread/media/"


# Full run
# time(./manage.py harvest --settings=mediathread.settings_test \
# --debug-mode --verbosity=2 --traceback)

# Run a particular file + scenario
# ./manage.py harvest \
# mediathread/main/features/manage_selection_visibility.feature \
# -d --settings=mediathread.settings_test -s 1

class ExceptionLoggingMiddleware(object):
    def process_exception(self, request, exception):
        import traceback
        print traceback.format_exc()

MIDDLEWARE_CLASSES.append(
    'mediathread.local_settings.ExceptionLoggingMiddleware',
    'mediathread.main.middleware.AuthRequirementMiddleware',
    'mediathread.course.middleware.CallToActionMiddleware',)

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False
}
