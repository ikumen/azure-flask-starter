import os
import unittest

from importlib import reload
from backend import settings
from backend.app import create_config_only_app
from unittest import mock

partial_prod_envvars = {
    'FLASK_ENV': 'production',
    'LOG_LVL': 'INFO',
    'DB_USERNAME': 'user',
}
full_prod_envvars = {
    **partial_prod_envvars,
    'FLASK_SECRET_KEY': 'secrets',
    'BLOB_STORE_URI': 'blob_store_uri',
    'BLOB_STORE_CREDENTIAL': 'blob_store_key',
    'DB_PASSWORD': 'pass',
    'DB_DATABASE': 'db',
    'DB_SERVER_HOST':'localhost'
}


class ConfigTests(unittest.TestCase):
    def test_getbool_from_str(self):
        self.assertFalse(settings._getbool_from_str(None))
        self.assertFalse(settings._getbool_from_str(''))
        self.assertFalse(settings._getbool_from_str('xyz'))
        self.assertTrue(settings._getbool_from_str('t'))
        self.assertTrue(settings._getbool_from_str('1'))
        self.assertTrue(settings._getbool_from_str('true'))
        self.assertTrue(settings._getbool_from_str('T'))
        self.assertTrue(settings._getbool_from_str('y'))
        self.assertTrue(settings._getbool_from_str('yes'))
        self.assertTrue(settings._getbool_from_str('YES'))

    @mock.patch('os.environ.get', new=full_prod_envvars.get)
    def test_load_config_with_production(self):
        """Test loading config with all values present."""
        reload(settings)
        app = create_config_only_app()
        self.assertEqual(app.config['DB_USERNAME'], full_prod_envvars.get('DB_USERNAME'))
        self.assertEqual(app.config['LOG_LVL'], full_prod_envvars.get('LOG_LVL'))

    @mock.patch('os.environ.get', new=partial_prod_envvars.get)
    def test_load_config_with_missing_envvar(self):
        """Test loading config but missing some values from the environment."""
        with self.assertRaises(EnvironmentError):
            reload(settings)
            app = create_config_only_app()
    
    def test_load_config_default_is_development(self):
        """Test loading the config with DevelopmentConfig."""
        reload(settings)
        app = create_config_only_app()
        self.assertEqual(app.config['ENV'], 'development')
        self.assertEqual(app.config['DB_USERNAME'], settings.DevelopmentConfig().DB_USERNAME)

    @mock.patch('os.environ.get', new={'LOCAL_CFG': '../tests/backend/local.cfg'}.get)
    def test_load_config_local_override(self):
        """Test loading local config in addition to DevelopmentConfig."""
        reload(settings)
        app = create_config_only_app()
        self.assertEqual(app.config['ENV'], 'development')
        self.assertEqual(app.config['DB_USERNAME'], 'foobar') # dev_config.DB_USERNAME = 'SA'


if __name__ == '__main__':
    unittest.main()