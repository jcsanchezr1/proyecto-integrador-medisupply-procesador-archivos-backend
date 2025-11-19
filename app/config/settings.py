"""
Configuración de la aplicación - Estructura para manejar configuraciones
"""
import os


class Config:
    """Configuración base de la aplicación"""
    
    # Configuración básica
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', '8080'))
    
    # Configuración de la aplicación
    APP_NAME = 'MediSupply Video Processor Backend'
    APP_VERSION = '1.0.0'
    
    # Configuración de Google Cloud Platform
    GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'project-id')
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', None)
    
    # Configuración de Google Cloud Storage
    BUCKET_NAME = os.getenv('BUCKET_NAME', 'medisupply-bucket')
    BUCKET_FOLDER = os.getenv('BUCKET_FOLDER', 'sales-plan')
    SIGNING_SERVICE_ACCOUNT_EMAIL = os.getenv('SIGNING_SERVICE_ACCOUNT_EMAIL', '')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 500 * 1024 * 1024))  # 500MB para videos
    
    # Configuración de la base de datos
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/medisupply')


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False


def get_config():
    """Retorna la configuración según el entorno"""
    env = os.getenv('FLASK_ENV', 'development').lower()
    
    if env == 'production':
        return ProductionConfig()
    else:
        return DevelopmentConfig()