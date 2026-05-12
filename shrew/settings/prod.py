from .base import *  # noqa

DEBUG = False
ALLOWED_HOSTS = ['shrew.app']

# In production we require a real secret key (base.py provides a placeholder
# default so tests and management commands work without a .env file; we
# explicitly override it here with a hard requirement).
SECRET_KEY = env('DJANGO_SECRET_KEY')

# Likewise, the database URL must be configured explicitly in production.
DATABASES = {
    'default': env.db('DJANGO_DATABASE_URL'),
}

# Security
SECURE_SSL_REDIRECT = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365 * 5  # 5 years

STATIC_ROOT = env.str("DJANGO_STATIC_ROOT")
MEDIA_ROOT = env.str("DJANGO_MEDIA_ROOT")
COMPRESS_OFFLINE = True

# These have safe empty defaults in base.py for tests/local dev; production
# must supply real values.
CLOUDCONVERT_KEY = env.str("DJANGO_CLOUDCONVERT_KEY")
RECAPTCHA_PUBLIC_KEY = env.str("DJANGO_RECAPTCHA_PUBLIC_KEY")
RECAPTCHA_PRIVATE_KEY = env.str("DJANGO_RECAPTCHA_PRIVATE_KEY")

ADMINS = [
    ('Ludwik', 'ludwik@gmail.com'),
]
MANAGERS = ADMINS

# Email
DEFAULT_FROM_EMAIL = SERVER_EMAIL = 'noreply@shrew.app'
EMAIL_SUBJECT_PREFIX = '[Code Shrew] '
EMAIL_HOST = env('DJANGO_EMAIL_HOST')
EMAIL_HOST_USER = env('DJANGO_EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('DJANGO_EMAIL_HOST_PASSWORD')
EMAIL_PORT = 465
EMAIL_USE_SSL = True
