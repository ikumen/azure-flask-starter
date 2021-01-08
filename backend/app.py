import logging
import urllib.parse

from flask import Flask, jsonify
from backend import settings, api, services, datastores


def create_config_only_app():
    """Produces a Flask app with only the settings configured. Serves
    as a base for test, manage, and regular app context.
    """
    app = Flask(__name__)

    # Load configurations
    config = settings.get_configs()
    app.config.from_object(config)
    # Optionally overwrite with using local configurations
    app.config.from_envvar('LOCAL_CFG', silent=True)

    # Check if any configurations are missing (e.g, is None) and fail fast
    missing_configs = []
    for attr in dir(config):
        if not attr.startswith('__') and attr.isupper() and app.config[attr] is None:
            missing_configs.append(attr)
    if missing_configs:
        raise EnvironmentError(f'Missing configurations: {missing_configs}')

    # These properties are dependent on other being set
    app.config['DB_ODBC_URI'] = f'DRIVER={app.config["DB_DRIVER"]};SERVER={app.config["DB_SERVER_HOST"]};PORT={app.config["DB_SERVER_PORT"]};DATABASE={app.config["DB_DATABASE"]};UID={app.config["DB_USERNAME"]};PWD={app.config["DB_PASSWORD"]}'
    app.config['SQLALCHEMY_DATABASE_URI'] =  f'mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(app.config["DB_ODBC_URI"])}'

    # Configure logging
    logging.basicConfig(level=app.config['APP_LOG_LVL'], 
        format='[%(asctime)s] [%(levelname)-8s] %(name)s: %(message)s')

    return app


def create_app():
    app = create_config_only_app()
    logging.getLogger('azure').setLevel(app.config['AZURE_LOG_LVL'])
    logging.getLogger('urllib3').setLevel(app.config['URLLIB_LOG_LVL'])
    
    datastores.db.init_app(app)
    datastores.blob_store.init_app(app)
    services.article_service.init_app(app)
    services.user_service.init_app(app)

    app.register_blueprint(api.bp)

    app.errorhandler(500)(lambda e: (jsonify(dict(error="Sorry, it's not you it's us!")), 500))
    app.errorhandler(404)(lambda e: (jsonify(dict(error="Doh")), 404))
    
    return app

    