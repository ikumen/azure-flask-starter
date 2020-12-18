"""
python manage.py db init 
python manage.py db migrate
python manage.py db upgrade
"""
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand, migrate
# Note models needs to be import so migration can detect tables defs
from backend import app, services, models


app = app.create_config_only_app()
services.db.init_app(app)

migrate = Migrate(app, services.db, 'alembic')
manager = Manager(app)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()