"""
Servicio de Google Cloud Storage para manejo de archivos
"""
import os
import logging
from typing import Optional, Tuple
from werkzeug.datastructures import FileStorage
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError
from io import BytesIO

from app.config.settings import Config

logger = logging.getLogger(__name__)


class CloudStorageService:
    """Servicio para manejar operaciones con Google Cloud Storage"""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self._client = None
        self._bucket = None
        
        logger.info(f"CloudStorageService inicializado - Bucket: {self.config.BUCKET_NAME}, Folder: {self.config.BUCKET_FOLDER}")
    
    @property
    def client(self) -> storage.Client:
        """Obtiene el cliente de Google Cloud Storage"""
        if self._client is None:
            try:
                # Configurar credenciales si están disponibles
                if self.config.GOOGLE_APPLICATION_CREDENTIALS:
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.config.GOOGLE_APPLICATION_CREDENTIALS
                
                self._client = storage.Client(project=self.config.GCP_PROJECT_ID)
            except Exception as e:
                raise GoogleCloudError(f"Error al inicializar cliente de GCS: {str(e)}")
        
        return self._client
    
    @property
    def bucket(self) -> storage.Bucket:
        """Obtiene el bucket de Google Cloud Storage"""
        if self._bucket is None:
            try:
                self._bucket = self.client.bucket(self.config.BUCKET_NAME)
            except Exception as e:
                raise GoogleCloudError(f"Error al obtener bucket '{self.config.BUCKET_NAME}': {str(e)}")
        
        return self._bucket
    
    def download_file(self, filename: str, folder: Optional[str] = None) -> BytesIO:
        """
        Descarga un archivo desde Google Cloud Storage
        
        Args:
            filename: Nombre del archivo a descargar
            folder: Carpeta donde se encuentra el archivo (opcional)
            
        Returns:
            BytesIO: Contenido del archivo en memoria
            
        Raises:
            GoogleCloudError: Si hay error al descargar el archivo
        """
        try:
            # Crear ruta completa con carpeta
            if folder:
                full_path = f"{folder}/{filename}"
            else:
                full_path = filename
            
            # Obtener blob del bucket
            blob = self.bucket.blob(full_path)
            
            # Verificar que el archivo existe
            if not blob.exists():
                raise GoogleCloudError(f"El archivo {full_path} no existe en el bucket")
            
            # Descargar archivo a memoria
            file_content = BytesIO()
            blob.download_to_file(file_content)
            file_content.seek(0)  # Volver al inicio del archivo
            
            logger.info(f"Archivo descargado exitosamente - Filename: {filename}")
            
            return file_content
            
        except GoogleCloudError as e:
            logger.error(f"Error de Google Cloud Storage: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error al descargar archivo: {str(e)}")
            raise GoogleCloudError(f"Error al descargar archivo desde Cloud Storage: {str(e)}")
    
    def file_exists(self, filename: str, folder: Optional[str] = None) -> bool:
        """
        Verifica si un archivo existe en Cloud Storage
        
        Args:
            filename: Nombre del archivo
            folder: Carpeta donde se encuentra el archivo (opcional)
            
        Returns:
            bool: True si el archivo existe, False en caso contrario
        """
        try:
            # Crear ruta completa con carpeta
            if folder:
                full_path = f"{folder}/{filename}"
            else:
                full_path = filename
            
            # Obtener blob del bucket
            blob = self.bucket.blob(full_path)
            
            return blob.exists()
            
        except Exception as e:
            logger.error(f"Error al verificar existencia del archivo: {str(e)}")
            return False
    
    def delete_file(self, filename: str, folder: Optional[str] = None) -> bool:
        """
        Elimina un archivo de Cloud Storage
        
        Args:
            filename: Nombre del archivo a eliminar
            folder: Carpeta donde se encuentra el archivo (opcional)
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            # Crear ruta completa con carpeta
            if folder:
                full_path = f"{folder}/{filename}"
            else:
                full_path = filename
            
            # Obtener blob del bucket
            blob = self.bucket.blob(full_path)
            
            if blob.exists():
                blob.delete()
                logger.info(f"Archivo eliminado exitosamente - Filename: {filename}")
                return True
            else:
                logger.warning(f"El archivo {full_path} no existe")
                return False
                
        except GoogleCloudError as e:
            logger.error(f"Error de Google Cloud Storage: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error al eliminar archivo: {str(e)}")
            return False
    
    def upload_file(self, file: FileStorage, filename: str, folder: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Sube un archivo de cualquier tipo al bucket de Google Cloud Storage
        
        Args:
            file: Archivo a subir
            filename: Nombre del archivo en el bucket
            folder: Carpeta donde guardar el archivo (opcional, usa config.BUCKET_FOLDER si no se especifica)
            
        Returns:
            Tuple[bool, str, Optional[str]]: (éxito, mensaje, url_pública)
        """
        try:
            if not file or not file.filename:
                return False, "No se proporcionó archivo", None
            
            # Verificar tamaño
            file.seek(0, 2)  # Ir al final del archivo
            file_size = file.tell()
            file.seek(0)  # Volver al inicio
            
            max_size = self.config.MAX_CONTENT_LENGTH
            if file_size > max_size:
                return False, f"El archivo excede el tamaño máximo permitido de {max_size // (1024*1024)} MB", None
            
            # Crear ruta completa con carpeta
            target_folder = folder if folder is not None else self.config.BUCKET_FOLDER
            full_path = f"{target_folder}/{filename}"
            
            # Crear blob en el bucket
            blob = self.bucket.blob(full_path)
            
            # Detectar content type
            content_type = 'application/octet-stream'
            if '.' in file.filename:
                extension = file.filename.split('.')[-1].lower()
                content_types = {
                    'pdf': 'application/pdf',
                    'doc': 'application/msword',
                    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'xls': 'application/vnd.ms-excel',
                    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'txt': 'text/plain',
                    'jpg': 'image/jpeg',
                    'jpeg': 'image/jpeg',
                    'png': 'image/png',
                    'gif': 'image/gif',
                    'mp4': 'video/mp4',
                    'avi': 'video/x-msvideo',
                    'mov': 'video/quicktime',
                    'wmv': 'video/x-ms-wmv'
                }
                content_type = content_types.get(extension, 'application/octet-stream')
            
            # Configurar metadatos
            blob.metadata = {
                'original_filename': file.filename,
                'content_type': content_type,
                'uploaded_by': 'medisupply-video-processor',
                'folder': target_folder
            }
            
            # Subir archivo
            file.seek(0)
            blob.upload_from_file(file, content_type=content_type)
            
            # Generar URL firmada
            signed_url = self.get_file_url(filename, folder=target_folder)
            
            logger.info(f"Archivo subido exitosamente - Filename: {filename}, Size: {file_size} bytes")
            
            return True, "Archivo subido exitosamente", signed_url
            
        except GoogleCloudError as e:
            return False, f"Error de Google Cloud Storage: {str(e)}", None
        except Exception as e:
            return False, f"Error al subir archivo: {str(e)}", None
    
    def get_file_url(self, filename: str, folder: Optional[str] = None, expiration_hours: int = 168) -> str:
        """
        Genera una URL firmada de un archivo en Cloud Storage usando impersonated credentials (Cloud Run safe)
        
        Args:
            filename: Nombre del archivo
            folder: Carpeta donde se encuentra el archivo (opcional, usa config.BUCKET_FOLDER si no se especifica)
            expiration_hours: Horas de validez de la URL (default: 168 = 7 días)
            
        Returns:
            str: URL firmada del archivo
        """
        try:
            from datetime import datetime, timedelta, timezone
            from google.auth import default, impersonated_credentials
            
            target_folder = folder if folder is not None else self.config.BUCKET_FOLDER
            full_path = f"{target_folder}/{filename}"
            blob = self.bucket.blob(full_path)

            if not blob.exists():
                logger.warning(f"El archivo {filename} no existe en el bucket")
                return ""

            expiration = datetime.now(timezone.utc) + timedelta(hours=expiration_hours)

            # Cargar credenciales actuales (las del Cloud Run service account)
            source_credentials, _ = default()

            # Impersonar el service account que firmará la URL
            target_credentials = impersonated_credentials.Credentials(
                source_credentials=source_credentials,
                target_principal=self.config.SIGNING_SERVICE_ACCOUNT_EMAIL,
                target_scopes=["https://www.googleapis.com/auth/devstorage.read_only"],
                lifetime=300,
            )

            # Generar la URL firmada usando las credenciales impersonadas
            signed_url = blob.generate_signed_url(
                expiration=expiration,
                method="GET",
                version="v4",
                credentials=target_credentials,
            )

            logger.info(f"URL firmada generada para {filename}")
            return signed_url

        except Exception as e:
            logger.error(f"Error al generar URL firmada para {filename}: {e}")
            return f"https://storage.googleapis.com/{self.config.BUCKET_NAME}/{target_folder}/{filename}"

