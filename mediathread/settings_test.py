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

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test',
    },
}

# Remove Johnny cache middleware
MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES[2:]

SESSION_ENGINE = "django.contrib.sessions.backends.file"

#ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_VERIFICATION = "optional"


LETTUCE_DJANGO_APP = ['lettuce.django']
INSTALLED_APPS = INSTALLED_APPS + LETTUCE_DJANGO_APP


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

#MIDDLEWARE_CLASSES.append(
#    'mediathread.settings_test.ExceptionLoggingMiddleware'
#)

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False
}

USTOMERIO_SITE_ID = '3af7cd0031ac680ac8c8'
CUSTOMERIO_API_KEY = 'de75f487148abf4f01f3'

SEGMENTIO_API_KEY = 'llrwwp6uvr'
SEGMENTIO_JS_KEY = 'llrwwp6uvr'

SOUTH_TESTS_MIGRATE = False
ACCOUNT_LOGOUT_ON_GET = True

CRISPY_TEMPLATE_PACK = 'bootstrap'

SESSION_EXPIRE_AT_BROWSER_CLOSE = False

DJANGOSHERD_FLICKR_APIKEY = '5ae43f2ccf372996beeb9d1d33121857'
SAMPLE_COURSE_ID = 1
SECRET_KEY = 'sadasdasd'
