"""
Test settings.

Uses SQLite (no PostgreSQL needed) and a non-DB cache so tests don't have
to run ``createcachetable``. Relies on the safe defaults in ``base.py``
for ``SECRET_KEY``, ``DJANGO_DATABASE_URL``, etc. - no env vars required.
"""
from .base import *  # noqa: F401,F403

DEBUG = False

# Force SQLite in-memory for tests regardless of any DATABASE_URL the user
# happens to have in their .env (base.py picks that up via django-environ).
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# django-recaptcha emits a system check error when keys are missing; silence
# it for tests. Real reCAPTCHA validation is not exercised here.
SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']

# In-memory email and cache backends keep tests hermetic and fast.
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# django-compressor needs STATIC_ROOT defined; tests don't actually write here.
import tempfile  # noqa: E402
STATIC_ROOT = tempfile.gettempdir() + '/shrew-test-static'
MEDIA_ROOT = tempfile.gettempdir() + '/shrew-test-media'

# Speed up password hashing in tests.
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
