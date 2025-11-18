"""
Pruebas unitarias para el servicio CloudStorageService
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
from google.cloud.exceptions import GoogleCloudError
from app.services.cloud_storage_service import CloudStorageService
from app.config.settings import Config


class TestCloudStorageService(unittest.TestCase):
    """Pruebas para el servicio CloudStorageService"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.config = Config()
        self.config.GCP_PROJECT_ID = 'test-project'
        self.config.BUCKET_NAME = 'test-bucket'
        self.config.BUCKET_FOLDER = 'test-folder'
        self.config.BUCKET_FOLDER_PROCESSED_PRODUCTS = 'processed_products'
    
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_service_initialization(self, mock_client_class):
        """Prueba la inicialización del servicio"""
        service = CloudStorageService(self.config)
        
        self.assertIsNotNone(service)
        self.assertEqual(service.config.BUCKET_NAME, 'test-bucket')
    
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_get_client(self, mock_client_class):
        """Prueba obtener el cliente de Cloud Storage"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        service = CloudStorageService(self.config)
        client = service.client
        
        self.assertIsNotNone(client)
        mock_client_class.assert_called_once_with(project=self.config.GCP_PROJECT_ID)
    
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_get_bucket(self, mock_client_class):
        """Prueba obtener el bucket"""
        mock_client = Mock()
        mock_bucket = Mock()
        mock_client.bucket.return_value = mock_bucket
        mock_client_class.return_value = mock_client
        
        service = CloudStorageService(self.config)
        bucket = service.bucket
        
        self.assertIsNotNone(bucket)
        mock_client.bucket.assert_called_once_with(self.config.BUCKET_NAME)
    
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_download_file_success(self, mock_client_class):
        """Prueba descargar archivo exitosamente"""
        # Configurar mocks
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        # Simular contenido del archivo
        file_content = b'SKU,Name,Quantity\nMED-1234,Test Product,100'
        mock_blob.exists.return_value = True
        mock_blob.download_to_file = lambda f: f.write(file_content)
        
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_client_class.return_value = mock_client
        
        # Ejecutar
        service = CloudStorageService(self.config)
        result = service.download_file('test_file.csv', 'processed_products')
        
        # Verificar
        self.assertIsInstance(result, BytesIO)
        content = result.read()
        self.assertEqual(content, file_content)
        mock_bucket.blob.assert_called_once_with('processed_products/test_file.csv')
    
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_download_file_not_found(self, mock_client_class):
        """Prueba descargar archivo que no existe"""
        # Configurar mocks
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        mock_blob.exists.return_value = False
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_client_class.return_value = mock_client
        
        # Ejecutar y verificar
        service = CloudStorageService(self.config)
        with self.assertRaises(GoogleCloudError) as context:
            service.download_file('non_existent.csv', 'processed_products')
        
        self.assertIn('no existe', str(context.exception))
    
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_download_file_without_folder(self, mock_client_class):
        """Prueba descargar archivo sin especificar carpeta"""
        # Configurar mocks
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        file_content = b'test content'
        mock_blob.exists.return_value = True
        mock_blob.download_to_file = lambda f: f.write(file_content)
        
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_client_class.return_value = mock_client
        
        # Ejecutar
        service = CloudStorageService(self.config)
        result = service.download_file('test_file.csv')
        
        # Verificar
        self.assertIsInstance(result, BytesIO)
        mock_bucket.blob.assert_called_once_with('test_file.csv')
    
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_file_exists_true(self, mock_client_class):
        """Prueba verificar que archivo existe"""
        # Configurar mocks
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        mock_blob.exists.return_value = True
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_client_class.return_value = mock_client
        
        # Ejecutar
        service = CloudStorageService(self.config)
        result = service.file_exists('existing_file.csv', 'processed_products')
        
        # Verificar
        self.assertTrue(result)
        mock_bucket.blob.assert_called_once_with('processed_products/existing_file.csv')
    
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_file_exists_false(self, mock_client_class):
        """Prueba verificar que archivo no existe"""
        # Configurar mocks
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        mock_blob.exists.return_value = False
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_client_class.return_value = mock_client
        
        # Ejecutar
        service = CloudStorageService(self.config)
        result = service.file_exists('non_existent.csv', 'processed_products')
        
        # Verificar
        self.assertFalse(result)
    
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_delete_file_success(self, mock_client_class):
        """Prueba eliminar archivo exitosamente"""
        # Configurar mocks
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        mock_blob.exists.return_value = True
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_client_class.return_value = mock_client
        
        # Ejecutar
        service = CloudStorageService(self.config)
        result = service.delete_file('file_to_delete.csv', 'processed_products')
        
        # Verificar
        self.assertTrue(result)
        mock_blob.delete.assert_called_once()
    
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_delete_file_not_found(self, mock_client_class):
        """Prueba eliminar archivo que no existe"""
        # Configurar mocks
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        mock_blob.exists.return_value = False
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_client_class.return_value = mock_client
        
        # Ejecutar
        service = CloudStorageService(self.config)
        result = service.delete_file('non_existent.csv', 'processed_products')
        
        # Verificar
        self.assertFalse(result)
        mock_blob.delete.assert_not_called()
    
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_download_file_error(self, mock_client_class):
        """Prueba error al descargar archivo"""
        # Configurar mocks
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        mock_blob.exists.return_value = True
        mock_blob.download_to_file.side_effect = GoogleCloudError("Download failed")
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_client_class.return_value = mock_client
        
        # Ejecutar y verificar
        service = CloudStorageService(self.config)
        with self.assertRaises(GoogleCloudError):
            service.download_file('error_file.csv', 'processed_products')
    
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_get_client_error(self, mock_client_class):
        """Prueba error al obtener cliente"""
        # Configurar mock para que falle
        mock_client_class.side_effect = Exception("Client initialization failed")
        
        # Ejecutar y verificar
        service = CloudStorageService(self.config)
        with self.assertRaises(GoogleCloudError) as context:
            _ = service.client
        
        self.assertIn("Error al inicializar cliente de GCS", str(context.exception))
    
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_get_bucket_error(self, mock_client_class):
        """Prueba error al obtener bucket"""
        # Configurar mocks
        mock_client = Mock()
        mock_client.bucket.side_effect = Exception("Bucket not found")
        mock_client_class.return_value = mock_client
        
        # Ejecutar y verificar
        service = CloudStorageService(self.config)
        with self.assertRaises(GoogleCloudError) as context:
            _ = service.bucket
        
        self.assertIn("Error al obtener bucket", str(context.exception))
    
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_file_exists_error(self, mock_client_class):
        """Prueba error al verificar existencia de archivo"""
        # Configurar mocks
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        mock_blob.exists.side_effect = Exception("Connection error")
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_client_class.return_value = mock_client
        
        # Ejecutar
        service = CloudStorageService(self.config)
        result = service.file_exists('some_file.csv', 'processed_products')
        
        # Verificar - debe retornar False en caso de error
        self.assertFalse(result)
    
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_delete_file_error(self, mock_client_class):
        """Prueba error al eliminar archivo"""
        # Configurar mocks
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        mock_blob.exists.return_value = True
        mock_blob.delete.side_effect = GoogleCloudError("Delete failed")
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_client_class.return_value = mock_client
        
        # Ejecutar
        service = CloudStorageService(self.config)
        result = service.delete_file('error_file.csv', 'processed_products')
        
        # Verificar - debe retornar False en caso de error
        self.assertFalse(result)
    
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_service_with_credentials(self, mock_client_class):
        """Prueba inicialización del servicio con credenciales"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Configurar credenciales
        self.config.GOOGLE_APPLICATION_CREDENTIALS = '/path/to/credentials.json'
        
        service = CloudStorageService(self.config)
        _ = service.client
        
        # Verificar que se llamó el cliente
        mock_client_class.assert_called_once_with(project=self.config.GCP_PROJECT_ID)
    
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_download_file_generic_error(self, mock_client_class):
        """Prueba error genérico al descargar archivo"""
        # Configurar mocks
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        mock_blob.exists.return_value = True
        mock_blob.download_to_file.side_effect = Exception("Generic error")
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_client_class.return_value = mock_client
        
        # Ejecutar y verificar
        service = CloudStorageService(self.config)
        with self.assertRaises(GoogleCloudError) as context:
            service.download_file('error_file.csv', 'processed_products')
        
        self.assertIn("Error al descargar archivo desde Cloud Storage", str(context.exception))
    
    @patch('app.services.cloud_storage_service.storage.Client')
    def test_delete_file_generic_error(self, mock_client_class):
        """Prueba error genérico al eliminar archivo"""
        # Configurar mocks
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        mock_blob.exists.return_value = True
        mock_blob.delete.side_effect = Exception("Generic error")
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_client_class.return_value = mock_client
        
        # Ejecutar
        service = CloudStorageService(self.config)
        result = service.delete_file('error_file.csv', 'processed_products')
        
        # Verificar
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()

