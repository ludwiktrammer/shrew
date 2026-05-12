#!/bin/sh
# Upgrade the Code Shrew production deployment in place.
#
# Run from the project root on the production host (MyDevil shared FreeBSD).
# Aborts on the first error so a half-applied deploy doesn't leave the site
# in a broken state.
set -eu

export DJANGO_SETTINGS_MODULE=shrew.settings.prod

# 1. Pull the latest code from master.
git pull origin master

# 2. Sync Python dependencies from uv.lock (no dev dependencies in prod).
uv sync --no-dev

# 3. Install/refresh JavaScript dependencies used by django-compressor.
npm install

# 4. Apply pending database migrations.
uv run --no-dev ./manage.py migrate --noinput

# 5. Compile and collect static assets.
#
# django-compressor offline mode needs two passes: the first pass renders
# templates and writes manifest files into the source tree; the second pass
# picks those up so collectstatic copies them to STATIC_ROOT. This mirrors
# the previous Pipenv-based upgrade script.
uv run --no-dev ./manage.py compress --force
uv run --no-dev ./manage.py collectstatic --noinput
uv run --no-dev ./manage.py compress --force
uv run --no-dev ./manage.py collectstatic --noinput

# 6. Tell Passenger to reload the application.
devil www restart shrew.app
