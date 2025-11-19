"""
Aplicación principal del procesador de videos MediSupply
"""
import os
from flask import Flask
from flask_restful import Api
from flask_cors import CORS


def create_app():
    """Factory function para crear la aplicación Flask"""
    
    app = Flask(__name__)
    
    # Configuración básica
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Configurar CORS
    cors = CORS(app)
    
    # Configurar rutas
    configure_routes(app)
    
    return app


def configure_routes(app):
    """Configura las rutas de la aplicación"""
    from .controllers.health_controller import HealthCheckView
    from .controllers.video_processor_controller import video_processor_bp
    
    api = Api(app)
    
    # Health check endpoint
    api.add_resource(HealthCheckView, '/files-procesor/ping')
    
    # Video processor endpoint
    app.register_blueprint(video_processor_bp)