from .base import *  # noqa

DEBUG = False
ALLOWED_HOSTS = ['shrew.app']

# Security
SECURE_SSL_REDIRECT = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365 * 5  # 5 years

STATIC_ROOT = env.str("DJANGO_STATIC_ROOT")
