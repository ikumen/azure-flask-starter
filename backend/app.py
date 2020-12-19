import logging

from flask import Flask, jsonify
from backend import settings, api, services


def create_config_only_app():
    app = Flask(__name__)

    # Load configurations
    config = settings.get_configs()
    app.config.from_object(config)
    app.config.from_envvar('LOCAL_CFG', silent=True)

    # Check if any configurations are missing (e.g, is None) and fail fast
    missing_configs = []
    for attr in dir(config):
        if not attr.startswith('__') and attr.isupper() and app.config[attr] is None:
            missing_configs.append(attr)
    if missing_configs:
        raise EnvironmentError(f'Missing configurations: {missing_configs}')

    # Configure logging
    logging.basicConfig(level=app.config['APP_LOG_LVL'], 
        format='[%(asctime)s] [%(levelname)-8s] %(name)s: %(message)s')

    return app


def create_app():
    app = create_config_only_app()
    logging.getLogger('azure').setLevel(app.config['AZURE_LOG_LVL'])
    logging.getLogger('urllib3').setLevel(app.config['URLLIB_LOG_LVL'])
    
    services.db.init_app(app)
    services.blob_store.init_app(app)
    services.article_service.init_app(app)
    services.user_service.init_app(app)

    app.register_blueprint(api.bp)

    app.errorhandler(500)(lambda e: (jsonify(dict(error="Sorry, it's not you it's us!")), 500))
    app.errorhandler(404)(lambda e: (jsonify(dict(error="Doh")), 404))
    
    return app

    