"""
Tests adicionales para VideoProcessorService (aumentar cobertura)
"""
import pytest
import sys
import os
import tempfile
from unittest.mock import Mock, MagicMock, patch, mock_open
from io import BytesIO
from datetime import datetime

# Mock moviepy antes de importar el servicio
sys.modules['moviepy'] = MagicMock()
sys.modules['moviepy.editor'] = MagicMock()
sys.modules['PIL'] = MagicMock()

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
    config.BUCKET_FOLDER_VIDEOS = 'test-videos'
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


class TestVideoProcessorServiceDownload:
    """Tests para _download_video_from_storage"""
    
    def test_download_video_success(self, video_processor_service, mock_cloud_storage_service):
        """Test de descarga exitosa"""
        filename = "test_video.mp4"
        mock_content = BytesIO(b"video content")
        mock_cloud_storage_service.download_file.return_value = mock_content
        
        result = video_processor_service._download_video_from_storage(filename)
        
        assert result == mock_content
        mock_cloud_storage_service.download_file.assert_called_once_with(
            filename,
            video_processor_service.config.BUCKET_FOLDER_VIDEOS
        )
    
    def test_download_video_error(self, video_processor_service, mock_cloud_storage_service):
        """Test de error al descargar"""
        filename = "test_video.mp4"
        mock_cloud_storage_service.download_file.side_effect = Exception("Download failed")
        
        with pytest.raises(Exception) as exc_info:
            video_processor_service._download_video_from_storage(filename)
        
        assert "Error al descargar video" in str(exc_info.value)


class TestVideoProcessorServiceUploadProcessed:
    """Tests para _upload_processed_video"""
    
    def test_upload_processed_video_success(self, video_processor_service, mock_cloud_storage_service):
        """Test de subida exitosa"""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            temp_file.write(b"processed video content")
            temp_path = temp_file.name
        
        try:
            filename = "test_processed.mp4"
            expected_url = "https://signed-url.com/test_processed.mp4"
            mock_cloud_storage_service.upload_file.return_value = (True, "Success", expected_url)
            
            result = video_processor_service._upload_processed_video(temp_path, filename)
            
            assert result == expected_url
            assert mock_cloud_storage_service.upload_file.called
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_upload_processed_video_failure(self, video_processor_service, mock_cloud_storage_service):
        """Test de fallo en subida"""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            temp_file.write(b"processed video content")
            temp_path = temp_file.name
        
        try:
            filename = "test_processed.mp4"
            mock_cloud_storage_service.upload_file.return_value = (False, "Upload failed", None)
            
            with pytest.raises(Exception) as exc_info:
                video_processor_service._upload_processed_video(temp_path, filename)
            
            assert "Error al subir video" in str(exc_info.value)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_upload_processed_video_file_not_found(self, video_processor_service):
        """Test con archivo que no existe"""
        nonexistent_path = "/path/to/nonexistent/file.mp4"
        filename = "test_processed.mp4"
        
        with pytest.raises(Exception) as exc_info:
            video_processor_service._upload_processed_video(nonexistent_path, filename)
        
        assert "Error al subir video procesado" in str(exc_info.value)


class TestVideoProcessorServiceUpdateRecord:
    """Tests para _update_visit_client_record"""
    
    def test_update_record_success(self, video_processor_service, mock_visit_repository):
        """Test de actualización exitosa"""
        visit_client_id = 1
        processed_filename = "video_processed.mp4"
        processed_url = "https://url.com/video_processed.mp4"
        
        # Mock del cliente
        mock_client = Mock(spec=ScheduledVisitClientDB)
        mock_visit_repository.session.query.return_value.filter.return_value.first.return_value = mock_client
        
        # Ejecutar
        video_processor_service._update_visit_client_record(
            visit_client_id,
            processed_filename,
            processed_url
        )
        
        # Verificar
        assert mock_client.filename_processed == processed_filename
        assert mock_client.filename_url_processed == processed_url
        assert mock_client.file_status == "Procesado"
        assert mock_visit_repository.session.commit.called
    
    def test_update_record_not_found(self, video_processor_service, mock_visit_repository):
        """Test con registro no encontrado"""
        visit_client_id = 999
        mock_visit_repository.session.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(Exception) as exc_info:
            video_processor_service._update_visit_client_record(
                visit_client_id,
                "file.mp4",
                "https://url.com"
            )
        
        assert "Registro no encontrado" in str(exc_info.value)
    
    def test_update_record_database_error(self, video_processor_service, mock_visit_repository):
        """Test de error en base de datos"""
        visit_client_id = 1
        mock_client = Mock(spec=ScheduledVisitClientDB)
        mock_visit_repository.session.query.return_value.filter.return_value.first.return_value = mock_client
        mock_visit_repository.session.commit.side_effect = Exception("DB Error")
        
        with pytest.raises(Exception) as exc_info:
            video_processor_service._update_visit_client_record(
                visit_client_id,
                "file.mp4",
                "https://url.com"
            )
        
        assert "Error al actualizar registro" in str(exc_info.value)
        assert mock_visit_repository.session.rollback.called


class TestVideoProcessorServiceCleanup:
    """Tests adicionales para _cleanup_temp_files"""
    
    def test_cleanup_multiple_files(self, video_processor_service):
        """Test de limpieza de múltiples archivos"""
        # Crear archivos temporales
        temp_files = []
        for i in range(3):
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'_{i}.mp4')
            temp_file.write(b"content")
            temp_file.close()
            temp_files.append(temp_file.name)
        
        # Limpiar
        video_processor_service._cleanup_temp_files(temp_files)
        
        # Verificar que se eliminaron
        for temp_path in temp_files:
            assert not os.path.exists(temp_path)
    
    def test_cleanup_with_none_paths(self, video_processor_service):
        """Test de limpieza con rutas None"""
        # No debe lanzar excepción
        video_processor_service._cleanup_temp_files([None, None])
    
    def test_cleanup_mixed_valid_invalid(self, video_processor_service):
        """Test de limpieza con rutas mixtas"""
        # Crear un archivo válido
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        temp_file.write(b"content")
        temp_file.close()
        valid_path = temp_file.name
        
        # Mezclar con rutas inválidas
        file_paths = [None, valid_path, "/nonexistent/path.mp4"]
        
        # No debe lanzar excepción
        video_processor_service._cleanup_temp_files(file_paths)
        
        # Verificar que el válido se eliminó
        assert not os.path.exists(valid_path)
    
    def test_cleanup_permission_error(self, video_processor_service):
        """Test de limpieza con error de permisos"""
        with patch('os.path.exists', return_value=True):
            with patch('os.remove', side_effect=PermissionError("No permission")):
                # No debe lanzar excepción, solo registrar warning
                video_processor_service._cleanup_temp_files(['/test/file.mp4'])


class TestVideoProcessorServiceProcessVideoIntegration:
    """Tests de integración para process_video_by_visit_client_id"""
    
    def test_process_video_complete_flow_with_error_in_download(
        self,
        video_processor_service,
        mock_visit_repository,
        mock_cloud_storage_service
    ):
        """Test de flujo completo con error en descarga"""
        visit_client_id = 1
        
        # Mock del cliente
        mock_client = Mock(spec=ScheduledVisitClientDB)
        mock_client.id = visit_client_id
        mock_client.filename = "test_video.mp4"
        mock_client.filename_url = "https://url.com/test_video.mp4"
        mock_visit_repository.session.query.return_value.filter.return_value.first.return_value = mock_client
        
        # Simular error en descarga
        mock_cloud_storage_service.download_file.side_effect = Exception("Download failed")
        
        # Ejecutar y verificar
        with pytest.raises(Exception) as exc_info:
            video_processor_service.process_video_by_visit_client_id(visit_client_id)
        
        assert "Error al procesar video" in str(exc_info.value)
    
    def test_process_video_with_cleanup_on_error(
        self,
        video_processor_service,
        mock_visit_repository
    ):
        """Test de que se limpia en caso de error"""
        visit_client_id = 1
        
        # Mock del cliente
        mock_client = Mock(spec=ScheduledVisitClientDB)
        mock_client.id = visit_client_id
        mock_client.filename = "test_video.mp4"
        mock_client.filename_url = "https://url.com/test_video.mp4"
        mock_visit_repository.session.query.return_value.filter.return_value.first.return_value = mock_client
        
        # Mock para simular error después de crear archivos temporales
        with patch.object(video_processor_service, '_download_video_from_storage') as mock_download:
            mock_download.side_effect = Exception("Error")
            
            with patch.object(video_processor_service, '_cleanup_temp_files') as mock_cleanup:
                # Ejecutar
                with pytest.raises(Exception):
                    video_processor_service.process_video_by_visit_client_id(visit_client_id)
                
                # Verificar que se intentó limpiar
                assert mock_cleanup.called


class TestVideoProcessorServiceGenerateFilename:
    """Tests adicionales para _generate_processed_filename"""
    
    def test_generate_filename_simple(self, video_processor_service):
        """Test con nombre simple"""
        result = video_processor_service._generate_processed_filename('video.mp4')
        assert result == 'video_processed.mp4'
    
    def test_generate_filename_with_path(self, video_processor_service):
        """Test con ruta completa"""
        result = video_processor_service._generate_processed_filename('/path/to/video.mp4')
        assert result == '/path/to/video_processed.mp4'
    
    def test_generate_filename_multiple_dots(self, video_processor_service):
        """Test con múltiples puntos en el nombre"""
        result = video_processor_service._generate_processed_filename('my.video.file.mp4')
        assert result == 'my.video.file_processed.mp4'


class TestVideoProcessorServiceGetVisitClientById:
    """Tests adicionales para _get_visit_client_by_id"""
    
    def test_get_visit_client_with_all_fields(self, video_processor_service, mock_visit_repository):
        """Test de obtención con todos los campos"""
        visit_client_id = 1
        
        mock_client = Mock(spec=ScheduledVisitClientDB)
        mock_client.id = visit_client_id
        mock_client.visit_id = "visit-123"
        mock_client.client_id = "client-456"
        mock_client.status = "SCHEDULED"
        mock_client.filename = "video.mp4"
        mock_client.filename_url = "https://url.com/video.mp4"
        mock_client.file_status = "Pending"
        mock_client.filename_processed = None
        mock_client.filename_url_processed = None
        
        mock_visit_repository.session.query.return_value.filter.return_value.first.return_value = mock_client
        
        result = video_processor_service._get_visit_client_by_id(visit_client_id)
        
        assert result == mock_client
        assert result.filename == "video.mp4"
        assert result.file_status == "Pending"


class TestVideoProcessorServiceCompleteFlow:
    """Tests para el flujo completo de procesamiento de video"""
    
    def test_process_video_complete_success_flow(self, video_processor_service, mock_visit_repository, mock_cloud_storage_service):
        """Test del flujo completo exitoso de procesamiento de video"""
        # Configurar mock del cliente
        mock_client = Mock()
        mock_client.id = 1
        mock_client.visit_id = "visit-123"
        mock_client.client_id = "client-456"
        mock_client.filename = "original.mp4"
        mock_client.filename_url = "https://example.com/original.mp4"
        mock_client.file_status = "Pendiente"
        
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_client
        mock_visit_repository.session.query.return_value = mock_query
        
        # Mock de descarga de video
        mock_video_content = BytesIO(b"video content")
        mock_cloud_storage_service.download_file.return_value = mock_video_content
        
        # Mock de procesamiento de video
        temp_video_path = "/tmp/temp_video.mp4"
        temp_processed_path = "/tmp/temp_processed.mp4"
        
        # Mock de subida de video procesado
        mock_cloud_storage_service.upload_file.return_value = (True, "Success", "https://example.com/processed.mp4")
        
        # Mock de commit
        mock_visit_repository.session.commit = Mock()
        
        with patch.object(video_processor_service, '_download_video_from_storage', return_value=mock_video_content):
            with patch.object(video_processor_service, '_process_video_with_logo', return_value=(temp_video_path, temp_processed_path)):
                with patch.object(video_processor_service, '_upload_processed_video', return_value="https://example.com/processed.mp4"):
                    with patch.object(video_processor_service, '_update_visit_client_record'):
                        with patch.object(video_processor_service, '_cleanup_temp_files'):
                            result = video_processor_service.process_video_by_visit_client_id(1)
        
        # Verificar resultado
        assert result['visit_client_id'] == 1
        assert result['original_filename'] == "original.mp4"
        assert result['processed_filename'] == "original_processed.mp4"
        assert result['processed_url'] == "https://example.com/processed.mp4"
        assert result['status'] == "Procesado"
    
    def test_process_video_with_error_in_processing(self, video_processor_service, mock_visit_repository, mock_cloud_storage_service):
        """Test cuando falla el procesamiento (no se actualiza file_status con error)"""
        # Configurar mock del cliente
        mock_client = Mock()
        mock_client.id = 1
        mock_client.filename = "original.mp4"
        mock_client.filename_url = "https://example.com/original.mp4"
        
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_client
        mock_visit_repository.session.query.return_value = mock_query
        
        # Mock de descarga que falla
        mock_cloud_storage_service.download_file.side_effect = Exception("Download failed")
        
        # No se debe actualizar file_status cuando hay error
        with patch.object(video_processor_service, '_cleanup_temp_files'):
            with pytest.raises(Exception, match="Error al procesar video"):
                video_processor_service.process_video_by_visit_client_id(1)


class TestVideoProcessorServiceProcessVideoWithLogo:
    """Tests para _process_video_with_logo"""
    
    def test_process_video_with_logo_no_logo_file(self, video_processor_service):
        """Test cuando el archivo del logo no existe"""
        video_content = BytesIO(b"fake video content")
        filename = "test_video.mp4"
        
        with patch('tempfile.NamedTemporaryFile') as mock_temp_file:
            mock_file = MagicMock()
            mock_file.name = '/tmp/temp_video.mp4'
            mock_file.__enter__.return_value = mock_file
            mock_temp_file.return_value = mock_file
            
            with patch('os.path.exists', return_value=False):
                with pytest.raises(Exception, match="Logo no encontrado"):
                    video_processor_service._process_video_with_logo(video_content, filename)

