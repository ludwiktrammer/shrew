# Code Shrew

## Installation (local development)

### Prerequisites

- [Python 3.6+](https://www.python.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [Pipenv](https://pipenv.org/)

### Installation instructions

1. Create a Pipenv environment and install Python dependencies:

        pipenv install --dev
        
2. Install JavaScript dependencies:

        npm install

3. Create and fill out file with local configuration variables:

       cp shrew/env.dev.example shrew/.env
    (alternatively you can set those settings as environment variables)

4. Run database migrations:

        pipenv run ./manage.py migrate
        
5. Create the admin account:

        pipenv run ./manage.py createsuperuser

6. Start the development server:

        pipenv run ./manage.py runserver
