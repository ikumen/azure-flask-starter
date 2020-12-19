# Azure Flask Starter

A simple [Flask](https://palletsprojects.com/p/flask/) starter project, with localized support for Azure backing services. 

## How is this starter different? 

If you find yourself here, then I'm assuming your goal is to eventually release your Flask application to Azure, possibly with dependencies on some Azure services. While you are developing the application, interacting/connecting to those Azure services can be tedious, slow, and costly. This starter project aims to simplify the development process by connecting to localized versions of Azure services&mdash;currently there is support for [SQL Database](https://docs.microsoft.com/en-us/azure/azure-sql/database/) and [Blob Storage](https://docs.microsoft.com/en-us/azure/storage/blobs/)&mdash;rather than connecting directly to the Azure cloud. 

The localized versions of the Azure services are functionally equivalent, not exact duplicates, but enough to simulate the backing services your application depends on. Thus allowing you to focus on developing the application, and less time provisioning and deprovisioning because you're worried about cost.

* [Quick Start](#quick-start)
* [Database Migrations](#database-migrations)
* [Testing](#testing)


## Quick Start

You should have: [Python 3.7 or later](https://www.python.org/downloads/), [pyenv](https://github.com/pyenv/pyenv), [Docker](https://docs.docker.com/get-docker/), and an IDE would be helpful ([Visual Studio Code is nice](https://code.visualstudio.com/)).

### Start SQL Database and Blob Storage

```bash
# Checkout the project and navigate to it
git clone git@github.com:ikumen/flask-azure-starter.git 
cd flask-azure-starter

# Start up the local SQL Server and Blob Storage
# May take from a 1-5mins depending on your connection
docker-compose up
...
```

### Setup Python and Initialize Database Schema
Open a second terminal and navigate to the project root.

```bash
cd /path/to/flask-azure-starter

# Setup Python, virtual environment, and install dependencies
echo "3.9.1" > .python-version
python -m venv .venv
. .venv/bin/activate
(.venv) pip install -r requirements.txt

# Initialize the database schema (e.g create tables)
(.venv) python manage.py db migrate
(.venv) python manage.py db upgrade
```

### Start the application
```bash
# Start the application
(.venv) python application.py
```

Congratulations, you can now check out your application at http://localhost:5000


_Note: If you're unfamiliar with any of the steps above, take a look at this [short introduction to setting up a Python project](https://gist.github.com/ikumen/132b753cee9050de9e56aa3834e82aab)._

## Database Migrations

Database schema creation and migrations are all handled by [SQLAlchemy](https://www.sqlalchemy.org/) and [Alembic](https://alembic.sqlalchemy.org/en/latest/). We use SQLAlchemy to abstract away the [low level database driver](https://pypi.org/project/pyodbc/) and help map our database schema to our models. Alembic is the tool that detects model changes and migrates them to our database schema. The workflow goes something like this:

1. initially we initialize the Alembic working directory `alembic`
1. start on the application side, and design your models and their relationships
1. when you're ready to test out the models against the database, use Alembic to detect the models, generate the schema
1. then use Alembic to apply the schema to the database, start up your app and test
1. repeat steps 2-4 as you develop and evolve your models, Alembic keeps track of all the changes your schema goes through as it evolves from the changes you make to your models.
1. finally everything in the `alembic` folder gets checked into source control, anyone that checks out the project can automatically migrate their local database to our latest schema

`manage.py` contains the hooks that tie your application models to Alembic, and exposes Alembic migration operations with a command line interface.

```bash
# This would normally be run just once at the start of the project
# to initialize the Alembic working directory, where it keeps the 
# migrations (see `alembic` folder).
(.venv) python manage.py db init

# After you make changes to your model, run this so Alembic detects the
# changes and updates the database schema to reflect mirror your models.
(.venv) python manage.py db migrate

# Finally run this to apply those changes to the database.
(.venv) python manage.py db upgrade
```

## Testing

```bash
(.venv) python -m unittest discover -p "*_tests.py"
```