import tempfile

from .base import *  # noqa


DEBUG = True

TEMPLATES[0]['OPTIONS']['debug'] = DEBUG
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Django Debug Toolbar
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]
INSTALLED_APPS += ['debug_toolbar', ]
INTERNAL_IPS = ['127.0.0.1', ]

STATIC_ROOT = os.path.join(tempfile.gettempdir(), 'shrew-static')
MEDIA_ROOT = os.path.join(tempfile.gettempdir(), 'shrew-media')
