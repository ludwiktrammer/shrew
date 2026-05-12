#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # Use test settings automatically when running ``./manage.py test`` so
    # contributors don't need to remember --settings=shrew.settings.test.
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shrew.settings.test")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shrew.settings.dev")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
