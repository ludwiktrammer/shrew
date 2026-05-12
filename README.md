# Code Shrew

## Installation (local development)

### Prerequisites

- [Python 3.12](https://www.python.org/) (uv can install this for you)
- [PostgreSQL](https://www.postgresql.org/)
- [uv](https://docs.astral.sh/uv/)

### Installation instructions

1. Install Python dependencies (this also creates a virtual environment in `.venv`):

        uv sync

2. Install JavaScript dependencies:

        npm install

3. Create and fill out file with local configuration variables:

       cp shrew/env.dev.example shrew/.env
    (alternatively you can set those settings as environment variables)

4. Run database migrations:

        uv run ./manage.py migrate

5. Create database table for keeping caches:

        uv run ./manage.py createcachetable

6. Create the admin account:

        uv run ./manage.py createsuperuser

7. Start the development server:

        uv run ./manage.py runserver

### Running tests

Tests use `shrew/settings/test.py` automatically (SQLite, in-memory cache; no `.env`, PostgreSQL or other setup required):

        uv run ./manage.py test tests

## Deployment

The project is deployed to a MyDevil (FreeBSD) shared host. Astral does
not ship a FreeBSD binary of `uv`, but MyDevil preinstalls
[Mise](https://wiki.mydevil.net/Mise/), which can install Rust so that
`uv` can be built from source via Cargo.

One-time setup on the server (run via SSH):

1. Enable [Binexec](https://wiki.mydevil.net/Binexec/) so the account is
   allowed to execute user-installed binaries.

2. Install Rust through Mise and add it to `PATH`:

        TMPDIR=~/.tmp mise install rust@stable
        mise env -s bash rust@stable >> ~/.bash_profile
        source ~/.bash_profile

3. Build and install `uv` from source via Cargo (takes ~10 min):

        cargo install --locked uv

   `~/.cargo/bin` should already be on `PATH` thanks to step 2. Verify:

        uv --version

Per-deployment steps (from the project directory):

4. Install Python dependencies into a `.venv` matching `uv.lock`:

        uv sync --no-dev

5. Run database migrations, create the cache table, and collect static files:

        uv run --no-dev ./manage.py migrate --settings=shrew.settings.prod
        uv run --no-dev ./manage.py createcachetable --settings=shrew.settings.prod
        uv run --no-dev ./manage.py collectstatic --settings=shrew.settings.prod --noinput

6. In the DevilWEB panel, set the Python interpreter for the domain to
   `.venv/bin/python` and point Passenger at `passenger_wsgi.py`.
