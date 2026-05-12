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
