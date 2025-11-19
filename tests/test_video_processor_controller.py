"""
Tests para el controlador de procesamiento de videos
"""
import pytest
import sys
import json
import base64
from unittest.mock import Mock, patch, MagicMock
from flask import Flask

# Mock moviepy antes de importar el controlador
sys.modules['moviepy'] = MagicMock()
sys.modules['moviepy.editor'] = MagicMock()

from app.controllers.video_processor_controller import VideoProcessorController, video_processor_bp


@pytest.fixture
def app():
    """Fixture para crear la aplicación Flask"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(video_processor_bp)
    return app


@pytest.fixture
def client(app):
    """Fixture para crear el cliente de prueba"""
    return app.test_client()


@pytest.fixture
def mock_processor_service():
    """Mock del servicio de procesamiento de videos"""
    return Mock()


@pytest.fixture
def controller(mock_processor_service):
    """Instancia del controlador con mock del servicio"""
    return VideoProcessorController(processor_service=mock_processor_service)


class TestVideoProcessorController:
    """Tests para VideoProcessorController"""
    
    def test_initialization(self, controller):
        """Test de inicialización del controlador"""
        assert controller is not None
        assert controller.processor_service is not None
    
    def test_process_video_no_json(self, client):
        """Test cuando no se envía JSON"""
        response = client.post('/files-procesor/video', data='not json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'JSON' in data['message']
    
    def test_process_video_no_message(self, client):
        """Test cuando no hay campo 'message' en el JSON"""
        response = client.post('/files-procesor/video', json={'data': 'test'})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Pub/Sub' in data['message']
    
    def test_process_video_no_data(self, client):
        """Test cuando no hay campo 'data' en el mensaje"""
        response = client.post('/files-procesor/video', json={'message': {}})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'data' in data['message']
    
    def test_process_video_invalid_base64(self, client):
        """Test cuando el data no es base64 válido"""
        response = client.post('/files-procesor/video', json={
            'message': {'data': 'not-valid-base64!!!'}
        })
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_process_video_no_visit_client_id(self, client):
        """Test cuando no hay scheduled_visit_client_id en el evento"""
        event_data = json.dumps({'event_type': 'video_processing'})
        encoded_data = base64.b64encode(event_data.encode('utf-8')).decode('utf-8')
        
        response = client.post('/files-procesor/video', json={
            'message': {'data': encoded_data}
        })
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'scheduled_visit_client_id' in data['message']
    
    def test_process_video_invalid_visit_client_id(self, client):
        """Test cuando scheduled_visit_client_id no es un número"""
        event_data = json.dumps({'scheduled_visit_client_id': 'not-a-number'})
        encoded_data = base64.b64encode(event_data.encode('utf-8')).decode('utf-8')
        
        response = client.post('/files-procesor/video', json={
            'message': {'data': encoded_data}
        })
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'número entero' in data['message']
    
    @patch('app.controllers.video_processor_controller.VideoProcessorService')
    def test_process_video_success(self, mock_service_class, client):
        """Test de procesamiento exitoso"""
        # Configurar mock del servicio
        mock_service = Mock()
        mock_service.process_video_by_visit_client_id.return_value = {
            'visit_client_id': 1,
            'original_filename': 'test.mp4',
            'processed_filename': 'test_processed.mp4',
            'processed_url': 'https://example.com/test_processed.mp4',
            'status': 'Procesado'
        }
        mock_service_class.return_value = mock_service
        
        # Preparar evento
        event_data = json.dumps({
            'scheduled_visit_client_id': 1,
            'event_type': 'video_processing'
        })
        encoded_data = base64.b64encode(event_data.encode('utf-8')).decode('utf-8')
        
        # Ejecutar
        response = client.post('/files-procesor/video', json={
            'message': {'data': encoded_data}
        })
        
        # Verificar
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert data['data']['visit_client_id'] == 1
    
    @patch('app.controllers.video_processor_controller.VideoProcessorService')
    def test_process_video_service_error(self, mock_service_class, client):
        """Test cuando el servicio lanza una excepción"""
        # Configurar mock del servicio para lanzar excepción
        mock_service = Mock()
        mock_service.process_video_by_visit_client_id.side_effect = Exception("Error de prueba")
        mock_service_class.return_value = mock_service
        
        # Preparar evento
        event_data = json.dumps({
            'scheduled_visit_client_id': 1,
            'event_type': 'video_processing'
        })
        encoded_data = base64.b64encode(event_data.encode('utf-8')).decode('utf-8')
        
        # Ejecutar
        response = client.post('/files-procesor/video', json={
            'message': {'data': encoded_data}
        })
        
        # Verificar
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Error' in data['message']

