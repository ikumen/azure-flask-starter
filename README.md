# Udacity ND081 Article CMS Project Refactor


[Jump down to original README.md](#article-cms-flaskwebproject)

## Tasks

- [x] [document a project setup](#project-setup)
- [x] complete original requirements ([see README.md below](#article-cms-flaskwebproject))
- [ ] separate development vs production environment
- [ ] add vanilla SQL&mdash;SQLAlchemy (like most ORM) is awesome, but at some point you're gonna need to hand craft some SQL queries because you can't get the ORM to work it's magic
- [ ] separate backend vs frontend
  - [ ] backend will serve API
  - [ ] frontend will consume the API
- [ ] add additional OAuth providers
- [ ] add SQL migration (at least document it)
- [ ] add tests (at least some examples)

## Project Setup

This is specifically about setting up for a Python project. Note, I'm still learning Python&mdash;so feel free to correct/point me in the direction to becoming more [Pythonic](https://www.google.com/search?client=firefox-b-1-d&q=pythonic). 

You'll need the following tools

- [pyenv](https://github.com/pyenv/pyenv) - At some point, you'll may need to have multiple versions of Python running. `pyenv` helps you manage and switch between versions without really messing up your environment
- [virtualenv](https://virtualenv.pypa.io/en/latest/) (for Python 2 users), otherwise Python 3 (as of 3.3) has virtual environment support built in. Every project has dependencies, many projects will have overlapping dependencies&mdash;with different versions. You use "virtual" environments to isolate each projects dependencies from each other. 
- [pip](https://pip.pypa.io/en/stable/) is the tool for installing dependencies&mdash;convention is to store the dependencies in a `requirements.txt` at the root of your project.

For every Python project, I do the following to set up my development environment. Make sure you're at the project root directory.

Determine the Python version I'm using and switch my shell to it via [pyenv](https://github.com/pyenv/pyenv) or add a `.python-version` at the project root for `pyenv` to pick up
```bash
# only applies to current shell
pyenv shell 3.7.1
# applies to current directory and sub directories (preferred method)
echo "3.8.3" > .python-version
```
Initialize a virtual environment (I prefer the hidden directory since you don't really need to do any work inside the `.venv` directory)
```bash
# if you're using Python 2
virtualenv .venv
# and Python 3 version
python -m venv .venv

# .. don't forget to activate it
. .venv/bin/activate
# your prompt will change to display the virtual environment
(.venv)
```
Next, install the dependencies&mdash;make sure you're in your virtual environment by looking for the `(.venv)` at the start of your prompt
```bash
# if it's a project with an existing requirements.txt
(.venv) pip install -r requirements.txt

# as you add more dependencies
(.venv) pip install flask
# make sure to update your requirements.txt, note this method will clobber the existing requirements file
(.venv) pip freeze > requirements.txt
```
Finally, make sure you have a [Python specific](https://github.com/github/gitignore/blob/master/Python.gitignore) [`.gitignore`](https://github.com/github/gitignore) for your project.


## Completing Original Project 

I finished the [project rubric/requirements](https://review.udacity.com/#!/rubrics/2850/view), and it was pretty straight forward&mdash;your views/results may vary depending on your environment and prior development experience. The course was pretty light in terms of app development, more focused on introducing Azure's services and integration with our project app. Overall I thought it was pretty good, but did have the following issues.

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

# hardcode the driver location in our URI
SQLALCHEMY_DATABASE_URI = 'mssql+pyodb....driver=/usr/local/lib/libmsodbcsql.17.dylib'
```
_source: https://stackoverflow.com/questions/44527452/cant-open-lib-odbc-driver-13-for-sql-server-sym-linking-issue_
* using `https` with localhost was a pain, Microsoft Edge wouldn't open it, and Firefox kept prompting me to accept the risk&mdash;will investigate.



------

# Article CMS (FlaskWebProject)

This project is a Python web application built using Flask. The user can log in and out and create/edit articles. An article consists of a title, author, and body of text stored in an Azure SQL Server along with an image that is stored in Azure Blob Storage. You will also implement OAuth2 with Sign in with Microsoft using the `msal` library, along with app logging.

## Log In Credentials for FlaskWebProject

- Username: admin
- Password: pass

Or, once the MS Login button is implemented, it will automatically log into the `admin` account.

## Project Instructions (For Student)

You are expected to do the following to complete this project:
1. Create a Resource Group in Azure.
2. Create an SQL Database in Azure that contains a user table, an article table, and data in each table (populated with the scripts provided in the SQL Scripts folder).
    - Provide a screenshot of the populated tables as detailed further below.
3. Create a Storage Container in Azure for `images` to be stored in a container.
    - Provide a screenshot of the storage endpoint URL as detailed further below.
4. Add functionality to the Sign In With Microsoft button. 
    - This will require completing TODOs in `views.py` with the `msal` library, along with appropriate registration in Azure Active Directory.
5. Choose to use either a VM or App Service to deploy the FlaskWebProject to Azure. Complete the analysis template in `WRITEUP.md` (or include in the README) to compare the two options, as well as detail your reasoning behind choosing one or the other. Once you have made your choice, go through with deployment.
6. Add logging for whether users successfully or unsuccessfully logged in.
    - This will require completing TODOs in `__init__.py`, as well as adding logging where desired in `views.py`.
7. To prove that the application in on Azure and working, go to the URL of your deployed app, log in using the credentials in this README, click the Create button, and create an article with the following data:
	- Title: "Hello World!"
	- Author: "Jane Doe"
	- Body: "My name is Jane Doe and this is my first article!"
	- Upload an image of your choice. Must be either a .png or .jpg.
   After saving, click back on the article you created and provide a screenshot proving that it was created successfully. Please also make sure the URL is present in the screenshot.
8. Log into the Azure Portal, go to your Resource Group, and provide a screenshot including all of the resources that were created to complete this project. (see sample screenshot in "example_images" folder)
9. Take a screenshot of the Redirect URIs entered for your registered app, related to the MS Login button.
10. Take a screenshot of your logs (can be from the Log stream in Azure) showing logging from an attempt to sign in with an invalid login, as well as a valid login.

## example_images Folder

This folder contains sample screenshots that students are required to submit in order to prove they completed various tasks throughout the project.

1. article-cms-solution.png is a screenshot from running the FlaskWebProject on Azure and prove that the student was able to create a new entry. The Title, Author, and Body fields must be populated to prove that the data is being retrieved from the Azure SQL Database while the image on the right proves that an image was uploaded and pulled from Azure Blob Storage.
2. azure-portal-resource-group.png is a screenshot from the Azure Portal showing all of the contents of the Resource Group the student needs to create. The resource group must (at least) contain the following:
	- Storage Account
	- SQL Server
	- SQL Database
	- Resources related to deploying the app
3. sql-storage-solution.png is a screenshot showing the created tables and one query of data from the initial scripts.
4. blob-solution.png is a screenshot showing an example of blob endpoints for where images are sent for storage.
5. uri-redirects-solution.png is a screenshot of the redirect URIs related to Microsoft authentication.
6. log-solution.png is a screenshot showing one potential form of logging with an "Invalid login attempt" and "admin logged in successfully", taken from the app's Log stream. You can customize your log messages as you see fit for these situations.

## Dependencies

1. A free Azure account
2. A GitHub account
3. Python 3.7 or later
4. Visual Studio 2019 Community Edition (Free)
5. The latest Azure CLI (helpful; not required - all actions can be done in the portal)

All Python dependencies are stored in the requirements.txt file. To install them, using Visual Studio 2019 Community Edition:
1. In the Solution Explorer, expand "Python Environments"
2. Right click on "Python 3.7 (64-bit) (global default)" and select "Install from requirements.txt"

## Troubleshooting

- Mac users may need to install `unixodbc` as well as related drivers as shown below:
    ```bash
    brew install unixodbc
    ```
- Check [here](https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/install-microsoft-odbc-driver-sql-server-macos?view=sql-server-ver15) to add SQL Server drivers for Mac.