# Udacity ND081 Article CMS Project Refactor


## Tasks

- [x] [project setup](#project-setup)
- [x] [complete original requirements](#completing-original-project) ([see original README.md below](#article-cms-flaskwebproject))
- [ ] isolate development/production configurations
- [ ] add vanilla SQL&mdash;SQLAlchemy (like most ORM) is awesome, but at some point you're gonna need to hand craft some SQL queries because you can't get the ORM to work it's magic
- [ ] separate backend vs frontend
  - [ ] backend will serve API
  - [ ] frontend will consume the API
- [ ] add additional OAuth providers
- [ ] add SQL migration (at least document it)
- [ ] add tests (at least some examples)

## Project Setup

### Python

I'm still learning Python&mdash;so feel free to correct/point me in the direction to becoming more [Pythonic](https://www.google.com/search?client=firefox-b-1-d&q=pythonic). 

You'll need the following tools

- [pyenv](https://github.com/pyenv/pyenv), at some point you'll may need to have multiple versions of Python running. `pyenv` helps you manage and switch between versions without really messing up your environment
- [virtualenv](https://virtualenv.pypa.io/en/latest/) (for Python 2 users), otherwise Python 3 (as of 3.3) has virtual environment support built in. Every project has dependencies, many projects will have overlapping dependencies&mdash;with different versions. You use "virtual" environments to isolate each projects dependencies from each other. 
- [pip](https://pip.pypa.io/en/stable/) is the tool for installing dependencies&mdash;convention is to store the dependencies in a `requirements.txt` at the root of your project.

For most Python projects, I use the following process to set up my development environment. Make sure you're at the project root directory.

Determine the Python version you will use and switch to it via [pyenv](https://github.com/pyenv/pyenv) `shell` or add a `.python-version` at the project root for `pyenv` to pick up

```bash
# only applies to current shell
pyenv shell 3.7.1
# applies to current directory and sub directories (preferred method)
echo "3.8.3" > .python-version
```

Initialize a virtual environment (I prefer to keep this directory hidden since it's managed by virtualenv).

```bash
# if you're using Python 2
virtualenv .venv
# and Python 3 version
python -m venv .venv

# .. don't forget to activate it
source .venv/bin/activate
# your prompt will change to display the virtual environment
(.venv)
```

Next, install the dependencies&mdash;make sure you're in the virtual environment by looking for the `(.venv)` at the start of your prompt

```bash
# if it's a project with an existing requirements.txt
(.venv) pip install -r requirements.txt

# as you add more dependencies
(.venv) pip install flask
# make sure to update your requirements.txt, note this method will clobber the existing requirements file
(.venv) pip freeze > requirements.txt
```

Finally, make sure you have a [Python specific](https://github.com/github/gitignore/blob/master/Python.gitignore) [`.gitignore`](https://github.com/github/gitignore) for your project.

### Emulators / Docker


TODO

## Completing Original Project 

I finished the [project rubric/requirements](https://review.udacity.com/#!/rubrics/2850/view), and thought it was pretty good. The course was light in terms of app development&mdash;the focus was on introducing Azure's services and integrating it with the project app. I did have the following issues.

- I couldn't get the app to connect to SQL database using the recommended approaches (for Mac OSX). I ended up hard coding the driver path just to get it working. 
```bash
# find where odbcinst.ini is installed
odbcinst -j

> unixODBC 2.3.9
> DRIVERS............: /usr/local/etc/odbcinst.ini
> SYSTEM DATA SOURCES: /usr/local/etc/odbc.ini
> FILE DATA SOURCES..: /usr/local/etc/
...

# open odbcinst.ini, and locate drive location
less /usr/local/etc/odbcinst.ini

> [ODBC Driver 17 for SQL Server]
> Description=Microsoft ODBC Driver 17 for SQL Server
> Driver=/usr/local/lib/libmsodbcsql.17.dylib
> UsageCount=1

# hardcode the driver location in the URI
SQLALCHEMY_DATABASE_URI = 'mssql+pyodb....driver=/usr/local/lib/libmsodbcsql.17.dylib'
```
_source: https://stackoverflow.com/questions/44527452/cant-open-lib-odbc-driver-13-for-sql-server-sym-linking-issue_

* using `https` with localhost was a pain, Microsoft Edge wouldn't open it, and Firefox kept prompting me to accept the risk.

At this point, we have the completed project and a base for where the refactoring will start. I've tagged it in the repository for reference.

## Isolate Development/Production Configurations

I like localizing development as much as possible. I realize the course is mostly about developing applications for Azure, and the exercises are using quick and simple apps to teach a concept, but it's messy connecting to Azure during development and it's easy to mix up variables from two environments. 

```python
# config.py
class Config:
    # What if we forget to set `SECRET_KEY` in production
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-key'
    # ... but do remember to set BLOB_ACCOUNT
    BLOB_ACCOUNT = os.environ.get('BLOB_ACCOUNT') or 'abczyz'
    # it's not clear what's meant for production vs development
    ...
```

In refactoring this app, I want to demonstrate an application structure and environment that I would use&mdash;maybe you have some thing better, I'd appreciate your suggestions/comments. 

Ideally, deployed code should be the same across all environments, while configurations are environment specific&mdash;switching environments should not require rebuilding the application. Our goal is something like the [twelve-factor](https://12factor.net/) method&mdash;keep all configs as [environment variables](https://en.wikipedia.org/wiki/Environment_variable) and completely agnostic of their environment&mdash;but it's hard managing configrations only in environment variables so we'll cheat :-). 

I modified `config.py` to explicitly load configurations from environment variables unless explicitly set&mdash;this happens for all environments outside of `development`. For `development`, configurations will be loaded from environment variables as well, but can also have a default value if not found as an environment variable. 

```python
# config.py
env = os.environ.get('FLASK_ENV', 'development')
is_development = env == 'development'

def envvar_with_devopt(key, opt=None):
    if is_development:
        return os.environ.get(key, opt)
    return os.environ.get(key)


class Config:
    # Each environment must set this attribute, 'development` can optionally 
    # use `ch3ez!ts` if variable not set as environment variable.
    SESSION_KEY = envvar_with_devopt('SECRET_KEY','ch3ez!ts')
    # Explicitly set, same across environments
    FLASK_SESSION_TYPE = 'filesystem'
    ..
```

We can control which environment we're in by passing [FLASK_ENV on startup](https://flask.palletsprojects.com/en/1.1.x/config/#environment-and-debug-features).

```bash
# We default FLASK_ENV to development, so you only 
# need to explicitly set for other environments. 
(.venv) FLASK_ENV=production python application.py
```

Another issue with the original `config.py` is the risk of exposing our secret keys/passwords if `config.py` was [accidentally checked in](https://qz.com/674520/companies-are-sharing-their-secret-access-codes-on-github-and-they-may-not-even-know-it/). For configurations that hold environment specific secrets/passwords, we simply set them using environment variables with no defaults, and either 1) set them as environment variables to be picked up or 2) load a special `local config` file, making sure not to check that file into source control.

```python
# config.py
class Config:
    ...
    # For secrets, simply load them from environment variables, no defaults
    OAUTH_CLIENT_SECRET = os.environ.get('OAUTH_CLIENT_SECRET')
    SQL_SERVER_PASSWORD = os.environ.get('SQL_SERVER_PASSWORD')


def init_app(app):
    # We load the Config into Flask
    app.config.from_object(Config)
    # at this point, we can either set the missing configs above as environment vars
    # or specify a file location that contains the missing configs using LOCAL_CFG.
    app.config.from_envvar('LOCAL_CFG', silent=True)
```

For example, if we kept the `OAUTH_CLIENT_SECRET` and `SQL_SERVER_PASSWORD` in a file called `local.cfg`

```python
# <project_root>/local.cfg
OAUTH_CLIENT_SECRET = 'speakeasy'
SQL_SERVER_PASSWORD = 'Tiger'
```

We can have the app load it with.

```bash
LOCAL_CFG=../local.cfg python application.py
```

We would add an entry for `local.cfg` in our `.gitignore` so it doesn't accidentally get checked in, but we can also simply move it out of the project directory&mdash;maybe a central directory where we keep all our development secret config files.

```bash
LOCAL_CFG=/etc/app-secrets/projectxxx.cfg python application.py
```

Finally, we need to make sure that all configurations are set and fail fast if any are missing.

```python
# config.py

def init_app(app):
    # Load configs
    app.config.from_object(Config)
    # and any local secret configs
    app.config.from_envvar('LOCAL_CFG', silent=True)

    # Check if any configurations are missing (e.g, None value)
    # and fail fast.
    missing_configs = []
    for attr in Config.__dict__.keys():
        if not attr.startswith('__') and app.config[attr] is None:
            missing_configs.append(attr)
    if missing_configs:
        raise KeyError(f'Missing configurations: {missing_configs}')
```


