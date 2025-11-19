"""
Pruebas unitarias para la configuración de la aplicación usando unittest
"""
import unittest
import sys
import os
from unittest.mock import patch

# Agregar el directorio padre al path para importar la app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.config.settings import Config, DevelopmentConfig, ProductionConfig, get_config


class TestConfig(unittest.TestCase):
    """Pruebas para la clase Config"""
    
    def test_config_has_secret_key(self):
        """Prueba que Config tiene SECRET_KEY"""
        self.assertTrue(hasattr(Config, 'SECRET_KEY'))
        self.assertIsNotNone(Config.SECRET_KEY)
    
    def test_config_has_debug(self):
        """Prueba que Config tiene DEBUG"""
        self.assertTrue(hasattr(Config, 'DEBUG'))
        self.assertIsInstance(Config.DEBUG, bool)
    
    def test_config_has_host(self):
        """Prueba que Config tiene HOST"""
        self.assertTrue(hasattr(Config, 'HOST'))
        self.assertIsNotNone(Config.HOST)
    
    def test_config_has_port(self):
        """Prueba que Config tiene PORT"""
        self.assertTrue(hasattr(Config, 'PORT'))
        self.assertIsInstance(Config.PORT, int)
    
    def test_config_has_app_name(self):
        """Prueba que Config tiene APP_NAME"""
        self.assertEqual(Config.APP_NAME, 'MediSupply Video Processor Backend')
    
    def test_config_has_app_version(self):
        """Prueba que Config tiene APP_VERSION"""
        self.assertEqual(Config.APP_VERSION, '1.0.0')
    
    @patch.dict(os.environ, {'SECRET_KEY': 'test-secret-key'})
    def test_config_reads_secret_key_from_env(self):
        """Prueba que Config lee SECRET_KEY de variables de entorno"""
        # Necesitamos reimportar para que lea la nueva variable de entorno
        import importlib
        from app.config import settings
        importlib.reload(settings)
        self.assertEqual(settings.Config.SECRET_KEY, 'test-secret-key')
    
    @patch.dict(os.environ, {'DEBUG': 'False'})
    def test_config_reads_debug_false_from_env(self):
        """Prueba que Config lee DEBUG=False de variables de entorno"""
        import importlib
        from app.config import settings
        importlib.reload(settings)
        self.assertFalse(settings.Config.DEBUG)
    
    @patch.dict(os.environ, {'DEBUG': 'True'})
    def test_config_reads_debug_true_from_env(self):
        """Prueba que Config lee DEBUG=True de variables de entorno"""
        import importlib
        from app.config import settings
        importlib.reload(settings)
        self.assertTrue(settings.Config.DEBUG)
    
    @patch.dict(os.environ, {'HOST': '127.0.0.1'})
    def test_config_reads_host_from_env(self):
        """Prueba que Config lee HOST de variables de entorno"""
        import importlib
        from app.config import settings
        importlib.reload(settings)
        self.assertEqual(settings.Config.HOST, '127.0.0.1')
    
    @patch.dict(os.environ, {'PORT': '5000'})
    def test_config_reads_port_from_env(self):
        """Prueba que Config lee PORT de variables de entorno"""
        import importlib
        from app.config import settings
        importlib.reload(settings)
        self.assertEqual(settings.Config.PORT, 5000)


class TestDevelopmentConfig(unittest.TestCase):
    """Pruebas para la clase DevelopmentConfig"""
    
    def test_development_config_inherits_from_config(self):
        """Prueba que DevelopmentConfig hereda de Config"""
        self.assertTrue(issubclass(DevelopmentConfig, Config))
    
    def test_development_config_has_debug_true(self):
        """Prueba que DevelopmentConfig tiene DEBUG=True"""
        self.assertTrue(DevelopmentConfig.DEBUG)
    
    def test_development_config_inherits_app_name(self):
        """Prueba que DevelopmentConfig hereda APP_NAME"""
        self.assertEqual(DevelopmentConfig.APP_NAME, 'MediSupply Video Processor Backend')
    
    def test_development_config_inherits_app_version(self):
        """Prueba que DevelopmentConfig hereda APP_VERSION"""
        self.assertEqual(DevelopmentConfig.APP_VERSION, '1.0.0')
    
    def test_development_config_can_be_instantiated(self):
        """Prueba que DevelopmentConfig se puede instanciar"""
        config = DevelopmentConfig()
        self.assertIsInstance(config, DevelopmentConfig)
        self.assertTrue(config.DEBUG)


class TestProductionConfig(unittest.TestCase):
    """Pruebas para la clase ProductionConfig"""
    
    def test_production_config_inherits_from_config(self):
        """Prueba que ProductionConfig hereda de Config"""
        self.assertTrue(issubclass(ProductionConfig, Config))
    
    def test_production_config_has_debug_false(self):
        """Prueba que ProductionConfig tiene DEBUG=False"""
        self.assertFalse(ProductionConfig.DEBUG)
    
    def test_production_config_inherits_app_name(self):
        """Prueba que ProductionConfig hereda APP_NAME"""
        self.assertEqual(ProductionConfig.APP_NAME, 'MediSupply Video Processor Backend')
    
    def test_production_config_inherits_app_version(self):
        """Prueba que ProductionConfig hereda APP_VERSION"""
        self.assertEqual(ProductionConfig.APP_VERSION, '1.0.0')
    
    def test_production_config_can_be_instantiated(self):
        """Prueba que ProductionConfig se puede instanciar"""
        config = ProductionConfig()
        self.assertIsInstance(config, ProductionConfig)
        self.assertFalse(config.DEBUG)


class TestGetConfig(unittest.TestCase):
    """Pruebas para la función get_config"""
    
    @patch.dict(os.environ, {'FLASK_ENV': 'development'})
    def test_get_config_returns_development_config(self):
        """Prueba que get_config retorna DevelopmentConfig cuando FLASK_ENV=development"""
        config = get_config()
        self.assertEqual(config.__class__.__name__, 'DevelopmentConfig')
        self.assertTrue(config.DEBUG)
    
    @patch.dict(os.environ, {'FLASK_ENV': 'production'})
    def test_get_config_returns_production_config(self):
        """Prueba que get_config retorna ProductionConfig cuando FLASK_ENV=production"""
        config = get_config()
        self.assertEqual(config.__class__.__name__, 'ProductionConfig')
        self.assertFalse(config.DEBUG)
    
    @patch.dict(os.environ, {'FLASK_ENV': 'PRODUCTION'})
    def test_get_config_is_case_insensitive(self):
        """Prueba que get_config es case-insensitive"""
        config = get_config()
        self.assertEqual(config.__class__.__name__, 'ProductionConfig')
        self.assertFalse(config.DEBUG)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_config_defaults_to_development(self):
        """Prueba que get_config retorna DevelopmentConfig por defecto"""
        # Limpiar FLASK_ENV si existe
        if 'FLASK_ENV' in os.environ:
            del os.environ['FLASK_ENV']
        config = get_config()
        self.assertEqual(config.__class__.__name__, 'DevelopmentConfig')
        self.assertTrue(config.DEBUG)
    
    @patch.dict(os.environ, {'FLASK_ENV': 'testing'})
    def test_get_config_returns_development_for_unknown_env(self):
        """Prueba que get_config retorna DevelopmentConfig para entornos desconocidos"""
        config = get_config()
        self.assertEqual(config.__class__.__name__, 'DevelopmentConfig')
        self.assertTrue(config.DEBUG)


if __name__ == '__main__':
    unittest.main()

