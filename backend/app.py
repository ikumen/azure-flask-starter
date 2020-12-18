import backend
import os
import importlib
import pkgutil
import logging

from flask import Flask, Blueprint
from backend import settings, api, services


def _register_blueprints(app, pkg_name, pkg_path):
    """Register Blueprints for given package."""
    for _, name, _ in pkgutil.iter_modules(pkg_path):
        m = importlib.import_module('%s.%s' % (pkg_name, name))
        for item in dir(m):
            item = getattr(m, item)
            if isinstance(item, Blueprint):
                app.register_blueprint(item)

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
    logging.basicConfig(level=app.config['LOG_LVL'], 
        format='[%(asctime)s] [%(levelname)-8s] %(name)s: %(message)s')

    return app


def create_app():
    app = create_config_only_app()
    
    services.db.init_app(app)
    services.blob_store.init_app(app)
    services.article_service.init_app(app)
    services.user_service.init_app(app)

    app.register_blueprint(api.bp)
    #_register_blueprints(app, app_name, [os.path.dirname(__file__)])
    
    return app

    