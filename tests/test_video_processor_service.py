"""
Tests para el servicio de procesamiento de videos
"""
import pytest
import sys
from unittest.mock import Mock, MagicMock, patch
from io import BytesIO

# Mock moviepy antes de importar el servicio
sys.modules['moviepy'] = MagicMock()
sys.modules['moviepy.editor'] = MagicMock()

from app.services.video_processor_service import VideoProcessorService
from app.models.db_models import ScheduledVisitClientDB


@pytest.fixture
def mock_visit_repository():
    """Mock del repositorio de visitas"""
    return Mock()


@pytest.fixture
def mock_cloud_storage_service():
    """Mock del servicio de Cloud Storage"""
    return Mock()


@pytest.fixture
def mock_config():
    """Mock de la configuración"""
    config = Mock()
    config.BUCKET_FOLDER = 'test-videos'
    config.MAX_CONTENT_LENGTH = 500 * 1024 * 1024
    return config


@pytest.fixture
def video_processor_service(mock_visit_repository, mock_cloud_storage_service, mock_config):
    """Instancia del servicio de procesamiento de videos con mocks"""
    return VideoProcessorService(
        visit_repository=mock_visit_repository,
        cloud_storage_service=mock_cloud_storage_service,
        config=mock_config
    )


class TestVideoProcessorService:
    """Tests para VideoProcessorService"""
    
    def test_initialization(self, video_processor_service, mock_config):
        """Test de inicialización del servicio"""
        assert video_processor_service is not None
        assert video_processor_service.config == mock_config
        assert video_processor_service.visit_repository is not None
        assert video_processor_service.cloud_storage_service is not None
    
    def test_get_visit_client_by_id_not_found(self, video_processor_service, mock_visit_repository):
        """Test cuando no se encuentra el registro"""
        # Configurar mock
        mock_visit_repository.session.query.return_value.filter.return_value.first.return_value = None
        
        # Ejecutar
        result = video_processor_service._get_visit_client_by_id(999)
        
        # Verificar
        assert result is None
    
    def test_get_visit_client_by_id_found(self, video_processor_service, mock_visit_repository):
        """Test cuando se encuentra el registro"""
        # Crear mock del cliente
        mock_client = Mock(spec=ScheduledVisitClientDB)
        mock_client.id = 1
        mock_client.filename = 'test_video.mp4'
        mock_client.filename_url = 'https://example.com/test_video.mp4'
        
        # Configurar mock
        mock_visit_repository.session.query.return_value.filter.return_value.first.return_value = mock_client
        
        # Ejecutar
        result = video_processor_service._get_visit_client_by_id(1)
        
        # Verificar
        assert result is not None
        assert result.id == 1
        assert result.filename == 'test_video.mp4'
    
    def test_generate_processed_filename(self, video_processor_service):
        """Test de generación de nombre de archivo procesado"""
        # Test con extensión .mp4
        result = video_processor_service._generate_processed_filename('video.mp4')
        assert result == 'video_processed.mp4'
        
        # Test con ruta completa
        result = video_processor_service._generate_processed_filename('path/to/video.mp4')
        assert result == 'path/to/video_processed.mp4'
        
        # Test con nombre complejo
        result = video_processor_service._generate_processed_filename('my_video_2024.mp4')
        assert result == 'my_video_2024_processed.mp4'
    
    def test_process_video_by_visit_client_id_not_found(self, video_processor_service, mock_visit_repository):
        """Test de procesamiento cuando no se encuentra el registro"""
        # Configurar mock
        mock_visit_repository.session.query.return_value.filter.return_value.first.return_value = None
        
        # Ejecutar y verificar excepción
        with pytest.raises(Exception) as exc_info:
            video_processor_service.process_video_by_visit_client_id(999)
        
        assert "No se encontró registro" in str(exc_info.value)
    
    def test_process_video_no_video_associated(self, video_processor_service, mock_visit_repository):
        """Test de procesamiento cuando no hay video asociado"""
        # Crear mock del cliente sin video
        mock_client = Mock(spec=ScheduledVisitClientDB)
        mock_client.id = 1
        mock_client.filename = None
        mock_client.filename_url = None
        
        # Configurar mock
        mock_visit_repository.session.query.return_value.filter.return_value.first.return_value = mock_client
        
        # Ejecutar y verificar excepción
        with pytest.raises(Exception) as exc_info:
            video_processor_service.process_video_by_visit_client_id(1)
        
        assert "no tiene un video asociado" in str(exc_info.value)
    
    @patch('os.path.exists')
    def test_cleanup_temp_files(self, mock_exists, video_processor_service):
        """Test de limpieza de archivos temporales"""
        mock_exists.return_value = True
        
        with patch('os.remove') as mock_remove:
            video_processor_service._cleanup_temp_files(['/tmp/file1.mp4', '/tmp/file2.mp4'])
            assert mock_remove.call_count == 2
    
    def test_cleanup_temp_files_nonexistent(self, video_processor_service):
        """Test de limpieza de archivos que no existen"""
        with patch('os.path.exists', return_value=False):
            with patch('os.remove') as mock_remove:
                video_processor_service._cleanup_temp_files(['/tmp/nonexistent.mp4'])
                mock_remove.assert_not_called()

