# Azure Flask Starter

A simple [Flask](https://palletsprojects.com/p/flask/) starter project, with localized support for Azure backing services. 

## How is this starter different? 

If you find yourself here, then I'm assuming your goal is to eventually release your Flask application to Azure, possibly with dependencies on some Azure services. While you are developing the application, interacting/connecting to those Azure services can be tedious, slow, and costly. This starter project aims to simplify the development process by connecting to localized versions of Azure services&mdash;currently there is support for [SQL Database](https://docs.microsoft.com/en-us/azure/azure-sql/database/) and [Blob Storage](https://docs.microsoft.com/en-us/azure/storage/blobs/)&mdash;rather than connecting directly to the Azure cloud. 

The localized versions of the Azure services are functionally equivalent, not exact duplicates, but enough to simulate the backing services your application depends on. Thus allowing you to focus on developing the application, and less time provisioning and deprovisioning because you're worried about cost.

* [Quick Start](#quick-start)
* [Database Migrations](#database-migrations)
* [Testing](#testing)


## Quick Start

You should have the following installed:

- [Python 3.7 or later](https://www.python.org/downloads/)
- [pyenv](https://github.com/pyenv/pyenv) (it's not needed, but makes life easier if you need to switch between Python versions)
- [Docker](https://docs.docker.com/get-docker/)
- [sqlcmd](https://docs.microsoft.com/en-us/sql/tools/sqlcmd-utility?view=sql-server-ver15)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- and an IDE would be helpful ([Visual Studio Code is nice](https://code.visualstudio.com/)).

### Start SQL Database and Blob Storage

```bash
# Checkout the project and navigate to it
git clone git@github.com:ikumen/azure-flask-starter.git
cd azure-flask-starter

# Start up the local SQL Server and Blob Storage
# May take from a 1-5mins depending on your connection
docker-compose up
...
```

### Setup Python and Initialize Database Schema
Open a second terminal and navigate to the project root.

```bash
cd /path/to/azure-flask-starter

# Setup Python, virtual environment, and install dependencies
echo "3.9.1" > .python-version
python -m venv .venv
. .venv/bin/activate
(.venv) pip install -r requirements.txt

# Initialize the database schema (e.g create tables)
(.venv) python manage.py db migrate
(.venv) python manage.py db upgrade
```

_Note: If you're unfamiliar with any of the steps above, take a look at this [short introduction to setting up a Python project](https://gist.github.com/ikumen/132b753cee9050de9e56aa3834e82aab)._

### Start the application
The moment of truth, let's start our application. :pray:
```bash
# Start the application
(.venv) python application.py
 ..
 * Serving Flask app "backend.app" (lazy loading)
 * Environment: development
 * Debug mode: on
 ...
```

If all went well, you should see above output after running `python application.py`, congratulations :+1:. 

### Verify the application is working

Let's hit some of the endpoints to make sure everything is working, open up a separate terminal.

```bash
# Hit the users endpoint
curl -i localhost:5000/api/users

> HTTP/1.0 200 OK
> Content-Type: application/json
> Content-Length: 3
> Server: Werkzeug/1.0.1 Python/3.8.3
> ...
>
> []

# As expected, no users. Let's add a user
curl -i localhost:5000/api/users \
-H "content-type: application/json" \
-d '{"name":"Daryl Zero"}'

> HTTP/1.0 400 BAD REQUEST
> Content-Type: application/json
> Content-Length: 60
> Server: Werkzeug/1.0.1 Python/3.8.3
> ...
>
> {
>   "error": "Missing required params: ['email']"
> }

# Oops, we forgot email, we did get a nice error 
# message. Let's try again.
curl -i localhost:5000/api/users \
-H "content-type: application/json" \
-d '{"name":"Daryl Zero", "email": "daryl@acme.org"}'

> HTTP/1.0 200 OK
> Content-Type: application/json
> Content-Length: 70
> Server: Werkzeug/1.0.1 Python/3.8.3
> ...
> 
> {
>   "email": "daryl@acme.org", 
>   "id": 1, 
>   "name": "Daryl Zero"
> }

# Awesome, let's add an article
curl -i localhost:5000/api/articles \
-F title="Getting started with Azure and Flask" \
-F user_id=1 -F image=@/path/to/image.png

> HTTP/1.1 100 Continue
> 
> HTTP/1.0 200 OK
> Content-Type: application/json
> Content-Length: 219
> Server: Werkzeug/1.0.1 Python/3.8.3
> ...
> 
> {
>   "content": "Lets do it", 
>   "created_at": "Sat, 11 Dec 2020 12:03:25 GMT", 
>   "id": 1, 
>   "image_filename": "02e30295-04bd-436b-b3ca-d0cc26b03cac.png", 
>   "title": "Getting started with Azure and Flask", 
>   "user_id": 1
> }
# Note: the image will be given a randomly generated name instead of what you uploaded
```

Great, we were able to add an article for our user and the associated image was saved to our blob storage. 

### Verify the data was saved to SQL Server and Blob Storage

Next, let's verify our data is in the database and blob storage using `sqlcmd` and the Azure cli `az`.

```bash
# First let's make sure our user was added to the database
sqlcmd -S localhost -U SA -P saPassw0rd -d localdb \
-Q "select * from users" -Y 20

> id          name                 email               
> ----------- -------------------- --------------------
>          1 Daryl Zero           daryl@acme.org    
>
> (1 row affected)

# Cool, next check if the article is there
sqlcmd -S localhost -U SA -P saPassw0rd -d localdb \
 -Q "select id, user_id, image_filename, title from articles" \
 -y 4 -Y 40

> id  user_id  image_filename                           title                      content             
> --- -------- ---------------------------------------- -------------------------- --------
>   1        1 02e30295-04bd-436b-b3ca-d0cc26b03cac.png Getting started with Az..  Lets do it

> (1 rows affected)


# Finally, we'll check blob storage for our article image. It should have the same name as the `image_filename` field above
az storage blob list -c articleassets \
--connection-string "AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;" \
--query "[].name"

> [
>   "02e30295-04bd-436b-b3ca-d0cc26b03cac.png"
> ]
```

Yeah, we made it!!! :tada: :clap: :+1: :metal:

Notes: If you checked out the project and ran it without changing any config in `settings.py`, then the above credentials for SQL Database and Blob Storage should work.

#### References for the commands above.

- [curl](https://curl.se/docs/manual.html)
- [sqlcmd](https://docs.microsoft.com/en-us/sql/tools/sqlcmd-utility?view=sql-server-ver15#command-line-options)
- [az storage blob](https://docs.microsoft.com/en-us/cli/azure/storage/blob?view=azure-cli-latest#az_storage_blob_list)

## Database Migrations

Database schema creation and migrations are all handled by [SQLAlchemy](https://www.sqlalchemy.org/) and [Alembic](https://alembic.sqlalchemy.org/en/latest/). We use SQLAlchemy to abstract away the [low level database driver](https://pypi.org/project/pyodbc/) and help map our database schema to our models. Alembic is the tool that detects model changes and migrates them to our database schema. The workflow goes something like this:

1. initialize the Alembic working directory `alembic` (performed once at start of project). _Note: we've gone ahead and provided an `alembic` directory for the starter, so you can skip this_
1. start on the application side, and design your models and their relationships
1. when you're ready to test out the models against the database, use Alembic to detect the models and generate the corresponding schema updates
1. then use Alembic to apply the schema updates to the database
1. start up your app and test against the new model and database schema
1. repeat steps 2-5 as you develop and evolve your models, Alembic keeps track of all the changes your schema goes through as it evolves from the changes you make to your models.
1. finally everything in the `alembic` folder gets checked into source control&mdash;anyone that checks out the project can now migrate our latest schema changes to their local database

To make working with Alembic easier, we've added `manage.py`. It contains the hooks that tie your application models to Alembic, and exposes Alembic migration operations with a command line interface.

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

`manage.py` uses the application config properties to connect to the same database instance the application does.

## Testing

```bash
(.venv) python -m unittest discover -p "*_tests.py"
```

## TODOs

- additional documentation
  - [how to deploy to Azure](https://github.com/ikumen/azure-flask-starter/issues/9)
  - [how config works](https://github.com/ikumen/azure-flask-starter/issues/10)
  - how Docker works and is being used
  - how models are encapsulated through the services
- [add login component](https://github.com/ikumen/azure-flask-starter/issues/12)
- [add demo frontend])(https://github.com/ikumen/azure-flask-starter/issues/11)