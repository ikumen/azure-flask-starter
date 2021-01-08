import os
import logging


def _getbool_from_str(s):
    """Convert the given s into bool value. Defaults to False"""
    try:
        return s.lower() in ['1','y','yes','t','true']
    except AttributeError:
        return False


def get_configs():
    env = os.environ.get('FLASK_ENV', 'development') 
    if env == 'development':
        return DevelopmentConfig() 
    return Config()


class Config:
    """Application wide configurations. Unless explicitly set, each configuration 
    is pull from environment variables.
    """
    DEBUG = _getbool_from_str(os.environ.get('FLASK_DEBUG')) # defaults to False
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    
    APP_LOG_LVL = os.environ.get('LOG_LVL')
    URLLIB_LOG_LVL = logging.INFO
    AZURE_LOG_LVL = logging.INFO

    CONTAINER_ARTICLE_ASSETS = "articleassets"

    BLOB_STORE_URI = os.environ.get('BLOB_STORE_URI')
    BLOB_STORE_CREDENTIAL = os.environ.get('BLOB_STORE_CREDENTIAL')
    BLOB_STORE_CONTAINERS = [CONTAINER_ARTICLE_ASSETS]

    DB_DRIVER = '{ODBC Driver 17 for SQL Server}'
    DB_SERVER_PORT = 1433
    DB_DATABASE = os.environ.get('DB_DATABASE')
    DB_USERNAME = os.environ.get('DB_USERNAME')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_SERVER_HOST = os.environ.get('DB_SERVER_HOST')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Moved to app.py/create_config_only_app, when DB_* properties are 
    # being overwritten by local file, this breaks
    # @property
    # def DB_ODBC_URI(self):
    #     return f'DRIVER={self.DB_DRIVER};SERVER={self.DB_SERVER_HOST};PORT={self.DB_SERVER_PORT};DATABASE={self.DB_DATABASE};UID={self.DB_USERNAME};PWD={self.DB_PASSWORD}'

    # @property
    # def SQLALCHEMY_DATABASE_URI(self):
    #     return f'mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(self.DB_ODBC_URI)}'


class DevelopmentConfig(Config):
    """Development environment specific overrides for Config.
    """
    ENV = 'development'
    DEBUG = True
    SECRET_KEY = 'che3z!ts'
    APP_LOG_LVL = logging.DEBUG
    URLLIB_LOG_LVL = logging.WARN
    AZURE_LOG_LVL = logging.WARN

    BLOB_STORE_URI = 'http://127.0.0.1:10000/devstoreaccount1'
    BLOB_STORE_CREDENTIAL = 'Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=='

    DB_USERNAME = 'SA'
    DB_PASSWORD = 'saPassw0rd'
    DB_DATABASE = 'localdb'
    DB_SERVER_HOST = 'localhost'

