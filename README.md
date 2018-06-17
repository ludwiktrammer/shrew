# Code Shrew

## Installation (local development)

### Prerequisites

- [Python 3.6+](https://www.python.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [Pipenv](https://pipenv.org/)

### Installation instructions

1. Create a Pipenv environment and install dependencies:

        pipenv install

2. Create and fill out file with local configuration variables:

       cp shrew/env.dev.example shrew/.env
    (alternatively you can set those settings as environment variables)

3. Run database migrations:

        pipenv run ./manage.py migrate
        
4. Create the admin account:

        pipenv run ./manage.py createsuperuser

5. Start the development server:

        pipenv run ./manage.py runserver
