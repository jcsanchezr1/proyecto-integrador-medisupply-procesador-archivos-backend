"""
Tests adicionales para CloudStorageService (métodos upload_file y get_file_url)
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from io import BytesIO
from werkzeug.datastructures import FileStorage
from google.cloud.exceptions import GoogleCloudError

from app.services.cloud_storage_service import CloudStorageService
from app.config.settings import Config


@pytest.fixture
def mock_config():
    """Mock de configuración"""
    config = Mock(spec=Config)
    config.BUCKET_NAME = 'test-bucket'
    config.BUCKET_FOLDER = 'test-folder'
    config.BUCKET_FOLDER_VIDEOS = 'videos'
    config.MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    config.SIGNING_SERVICE_ACCOUNT_EMAIL = 'test@example.com'
    config.GCP_PROJECT_ID = 'test-project'
    config.GOOGLE_APPLICATION_CREDENTIALS = None
    return config


@pytest.fixture
def service(mock_config):
    """Instancia del servicio con configuración mock"""
    return CloudStorageService(mock_config)


class TestCloudStorageServiceUploadFile:
    """Tests para el método upload_file"""
    
    def test_upload_file_success(self, service, mock_config):
        """Test de subida exitosa de archivo"""
        # Crear archivo mock
        content = b"test content"
        file = FileStorage(
            stream=BytesIO(content),
            filename='test.mp4',
            content_type='video/mp4'
        )
        
        # Mock del bucket y blob
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_bucket.blob.return_value = mock_blob
        mock_blob.exists.return_value = True
        
        # Mockear _bucket directamente para evitar inicialización del cliente
        service._bucket = mock_bucket
        with patch.object(service, 'get_file_url', return_value='https://signed-url.com'):
            # Ejecutar
            success, message, url = service.upload_file(file, 'test.mp4')
            
            # Verificar
            assert success is True
            assert "exitosamente" in message
            assert url == 'https://signed-url.com'
            assert mock_blob.upload_from_file.called
    
    def test_upload_file_no_file(self, service):
        """Test con archivo None"""
        success, message, url = service.upload_file(None, 'test.mp4')
        
        assert success is False
        assert "No se proporcionó archivo" in message
        assert url is None
    
    def test_upload_file_no_filename(self, service):
        """Test con archivo sin nombre"""
        file = Mock(spec=FileStorage)
        file.filename = None
        
        success, message, url = service.upload_file(file, 'test.mp4')
        
        assert success is False
        assert "No se proporcionó archivo" in message
        assert url is None
    
    def test_upload_file_exceeds_max_size(self, service, mock_config):
        """Test con archivo que excede el tamaño máximo"""
        # Crear archivo grande
        large_content = b"x" * (mock_config.MAX_CONTENT_LENGTH + 1)
        file = FileStorage(
            stream=BytesIO(large_content),
            filename='large.mp4'
        )
        
        success, message, url = service.upload_file(file, 'large.mp4')
        
        assert success is False
        assert "excede el tamaño máximo" in message
        assert url is None
    
    def test_upload_file_with_custom_folder(self, service):
        """Test de subida con carpeta personalizada"""
        content = b"test content"
        file = FileStorage(
            stream=BytesIO(content),
            filename='test.mp4'
        )
        
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_bucket.blob.return_value = mock_blob
        
        service._bucket = mock_bucket
        with patch.object(service, 'get_file_url', return_value='https://url.com'):
            # Ejecutar con carpeta personalizada
            success, message, url = service.upload_file(file, 'test.mp4', folder='custom-folder')
            
            # Verificar que se usó la carpeta personalizada
            mock_bucket.blob.assert_called_once()
            call_args = mock_bucket.blob.call_args[0][0]
            assert 'custom-folder' in call_args
    
    def test_upload_file_detects_content_type_mp4(self, service):
        """Test de detección de content type para MP4"""
        file = FileStorage(
            stream=BytesIO(b"content"),
            filename='video.mp4'
        )
        
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_bucket.blob.return_value = mock_blob
        
        service._bucket = mock_bucket
        with patch.object(service, 'get_file_url', return_value='https://url.com'):
            service.upload_file(file, 'video.mp4')
            
            # Verificar que se llamó upload_from_file con content_type correcto
            assert mock_blob.upload_from_file.called
            call_kwargs = mock_blob.upload_from_file.call_args[1]
            assert call_kwargs['content_type'] == 'video/mp4'
    
    def test_upload_file_detects_content_type_pdf(self, service):
        """Test de detección de content type para PDF"""
        file = FileStorage(
            stream=BytesIO(b"content"),
            filename='document.pdf'
        )
        
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_bucket.blob.return_value = mock_blob
        
        service._bucket = mock_bucket
        with patch.object(service, 'get_file_url', return_value='https://url.com'):
            service.upload_file(file, 'document.pdf')
            
            call_kwargs = mock_blob.upload_from_file.call_args[1]
            assert call_kwargs['content_type'] == 'application/pdf'
    
    def test_upload_file_unknown_extension(self, service):
        """Test con extensión desconocida"""
        file = FileStorage(
            stream=BytesIO(b"content"),
            filename='file.unknown'
        )
        
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_bucket.blob.return_value = mock_blob
        
        service._bucket = mock_bucket
        with patch.object(service, 'get_file_url', return_value='https://url.com'):
            service.upload_file(file, 'file.unknown')
            
            call_kwargs = mock_blob.upload_from_file.call_args[1]
            assert call_kwargs['content_type'] == 'application/octet-stream'
    
    def test_upload_file_gcs_error(self, service):
        """Test de error de Google Cloud Storage"""
        file = FileStorage(
            stream=BytesIO(b"content"),
            filename='test.mp4'
        )
        
        mock_bucket = Mock()
        mock_bucket.blob.side_effect = GoogleCloudError("GCS Error")
        
        service._bucket = mock_bucket
        success, message, url = service.upload_file(file, 'test.mp4')
        
        assert success is False
        assert "Google Cloud Storage" in message
        assert url is None
    
    def test_upload_file_generic_error(self, service):
        """Test de error genérico"""
        file = FileStorage(
            stream=BytesIO(b"content"),
            filename='test.mp4'
        )
        
        mock_bucket = Mock()
        mock_bucket.blob.side_effect = Exception("Generic Error")
        
        service._bucket = mock_bucket
        success, message, url = service.upload_file(file, 'test.mp4')
        
        assert success is False
        assert "Error al subir archivo" in message
        assert url is None


class TestCloudStorageServiceGetFileUrl:
    """Tests para el método get_file_url"""
    
    @patch('google.auth.default')
    @patch('google.auth.impersonated_credentials.Credentials')
    def test_get_file_url_success(self, mock_impersonated_creds, mock_default, service):
        """Test de generación exitosa de URL firmada"""
        # Mock de credenciales
        mock_source_creds = Mock()
        mock_default.return_value = (mock_source_creds, None)
        mock_target_creds = Mock()
        mock_impersonated_creds.return_value = mock_target_creds
        
        # Mock del bucket y blob
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_blob.exists.return_value = True
        mock_blob.generate_signed_url.return_value = 'https://signed-url.com'
        mock_bucket.blob.return_value = mock_blob
        
        service._bucket = mock_bucket
        # Ejecutar
        url = service.get_file_url('test.mp4')
        
        # Verificar
        assert url == 'https://signed-url.com'
        assert mock_blob.generate_signed_url.called
    
    def test_get_file_url_file_not_exists(self, service):
        """Test con archivo que no existe"""
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_blob.exists.return_value = False
        mock_bucket.blob.return_value = mock_blob
        
        service._bucket = mock_bucket
        url = service.get_file_url('nonexistent.mp4')
        
        assert url == ""
    
    def test_get_file_url_with_custom_folder(self, service):
        """Test con carpeta personalizada"""
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_blob.exists.return_value = False
        mock_bucket.blob.return_value = mock_blob
        
        service._bucket = mock_bucket
        service.get_file_url('test.mp4', folder='custom-folder')
        
        # Verificar que se usó la carpeta personalizada
        call_args = mock_bucket.blob.call_args[0][0]
        assert 'custom-folder/test.mp4' in call_args
    
    @patch('google.auth.default')
    @patch('google.auth.impersonated_credentials.Credentials')
    def test_get_file_url_with_custom_expiration(self, mock_impersonated_creds, mock_default, service):
        """Test con tiempo de expiración personalizado"""
        # Mock de credenciales
        mock_source_creds = Mock()
        mock_default.return_value = (mock_source_creds, None)
        mock_target_creds = Mock()
        mock_impersonated_creds.return_value = mock_target_creds
        
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_blob.exists.return_value = True
        mock_blob.generate_signed_url.return_value = 'https://url.com'
        mock_bucket.blob.return_value = mock_blob
        
        service._bucket = mock_bucket
        service.get_file_url('test.mp4', expiration_hours=24)
        
        # URL debería ser generada
        assert mock_blob.generate_signed_url.called
    
    @patch('google.auth.default')
    def test_get_file_url_error_fallback(self, mock_default, service):
        """Test de fallback cuando hay error"""
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_blob.exists.return_value = True
        mock_blob.generate_signed_url.side_effect = Exception("Error")
        mock_bucket.blob.return_value = mock_blob
        
        # Mock de credenciales default
        mock_source_creds = Mock()
        mock_default.return_value = (mock_source_creds, None)
        
        service._bucket = mock_bucket
        url = service.get_file_url('test.mp4', folder='videos')
        
        # Debería devolver URL pública como fallback
        assert service.config.BUCKET_NAME in url
        assert 'test.mp4' in url


class TestCloudStorageServiceUploadFileMetadata:
    """Tests para metadatos en upload_file"""
    
    def test_upload_file_sets_correct_metadata(self, service):
        """Test de que se establecen los metadatos correctos"""
        file = FileStorage(
            stream=BytesIO(b"content"),
            filename='original_name.mp4'
        )
        
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_bucket.blob.return_value = mock_blob
        
        service._bucket = mock_bucket
        with patch.object(service, 'get_file_url', return_value='https://url.com'):
            service.upload_file(file, 'stored_name.mp4', folder='videos')
            
            # Verificar metadatos
            assert mock_blob.metadata is not None
            assert mock_blob.metadata['original_filename'] == 'original_name.mp4'
            assert mock_blob.metadata['content_type'] == 'video/mp4'
            assert mock_blob.metadata['uploaded_by'] == 'medisupply-video-processor'
            assert mock_blob.metadata['folder'] == 'videos'


class TestCloudStorageServiceVideoFormats:
    """Tests para formatos de video soportados"""
    
    @pytest.mark.parametrize("filename,expected_content_type", [
        ('video.mp4', 'video/mp4'),
        ('video.avi', 'video/x-msvideo'),
        ('video.mov', 'video/quicktime'),
        ('video.wmv', 'video/x-ms-wmv'),
    ])
    def test_upload_file_video_formats(self, service, filename, expected_content_type):
        """Test de detección de formatos de video"""
        file = FileStorage(
            stream=BytesIO(b"content"),
            filename=filename
        )
        
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_bucket.blob.return_value = mock_blob
        
        service._bucket = mock_bucket
        with patch.object(service, 'get_file_url', return_value='https://url.com'):
            service.upload_file(file, filename)
            
            call_kwargs = mock_blob.upload_from_file.call_args[1]
            assert call_kwargs['content_type'] == expected_content_type


class TestCloudStorageServiceImageFormats:
    """Tests para formatos de imagen soportados"""
    
    @pytest.mark.parametrize("filename,expected_content_type", [
        ('image.jpg', 'image/jpeg'),
        ('image.jpeg', 'image/jpeg'),
        ('image.png', 'image/png'),
        ('image.gif', 'image/gif'),
    ])
    def test_upload_file_image_formats(self, service, filename, expected_content_type):
        """Test de detección de formatos de imagen"""
        file = FileStorage(
            stream=BytesIO(b"content"),
            filename=filename
        )
        
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_bucket.blob.return_value = mock_blob
        
        service._bucket = mock_bucket
        with patch.object(service, 'get_file_url', return_value='https://url.com'):
            service.upload_file(file, filename)
            
            call_kwargs = mock_blob.upload_from_file.call_args[1]
            assert call_kwargs['content_type'] == expected_content_type

