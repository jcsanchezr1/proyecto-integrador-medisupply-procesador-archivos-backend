"""
Servicio para procesar videos de visitas de clientes desde Cloud Storage
"""
import logging
import os
import tempfile
from typing import Dict, Any, Tuple
from datetime import datetime
from io import BytesIO

from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
from PIL import Image

from app.config.settings import Config
from app.repositories.scheduled_visit_repository import ScheduledVisitRepository
from app.services.cloud_storage_service import CloudStorageService

logger = logging.getLogger(__name__)


class VideoProcessorService:
    """
    Servicio para procesar videos de visitas de clientes desde Cloud Storage
    """
    
    def __init__(self, visit_repository=None, cloud_storage_service=None, config=None):
        self.config = config or Config()
        self.visit_repository = visit_repository
        self.cloud_storage_service = cloud_storage_service or CloudStorageService(self.config)
        self.logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'resources', 'logoMedisupply.png')
    
    def process_video_by_visit_client_id(self, visit_client_id: int) -> Dict[str, Any]:
        """
        Procesa un video de visita de cliente usando el visit_client_id
        
        Args:
            visit_client_id: ID del registro de cliente en visita
            
        Returns:
            Dict[str, Any]: Resultado del procesamiento
            
        Raises:
            Exception: Si hay errores en el procesamiento
        """
        temp_video_path = None
        temp_processed_path = None
        
        try:
            logger.info(f"Iniciando procesamiento de video - Visit Client ID: {visit_client_id}")
            
            # 1. Obtener el registro de cliente en visita desde la BD
            db_client = self._get_visit_client_by_id(visit_client_id)
            if not db_client:
                raise Exception(f"No se encontró registro de cliente en visita con ID: {visit_client_id}")
            
            # Validar que tenga un video asociado
            if not db_client.filename or not db_client.filename_url:
                raise Exception(f"El registro no tiene un video asociado")
            
            logger.info(f"Registro encontrado - File: {db_client.filename}")
            
            # 2. Descargar el video desde Cloud Storage
            video_content = self._download_video_from_storage(db_client.filename)
            
            # 3. Procesar el video (agregar logo en los primeros 3 segundos)
            temp_video_path, temp_processed_path = self._process_video_with_logo(
                video_content, 
                db_client.filename
            )
            
            # 4. Generar nombre del archivo procesado
            processed_filename = self._generate_processed_filename(db_client.filename)
            
            # 5. Subir el video procesado a Cloud Storage
            processed_url = self._upload_processed_video(temp_processed_path, processed_filename)
            
            # 6. Actualizar el registro en la base de datos
            self._update_visit_client_record(
                visit_client_id,
                processed_filename,
                processed_url
            )
            
            logger.info(f"Video procesado exitosamente - Original: {db_client.filename}, Procesado: {processed_filename}")
            
            return {
                "visit_client_id": visit_client_id,
                "original_filename": db_client.filename,
                "processed_filename": processed_filename,
                "processed_url": processed_url,
                "status": "Procesado"
            }
            
        except Exception as e:
            logger.error(f"Error en procesamiento de video: {str(e)}")
            
            # No actualizar file_status en caso de error, solo registrar el error
            # El file_status solo debe ser "Procesado" cuando el procesamiento es exitoso
            
            raise Exception(f"Error al procesar video: {str(e)}")
        
        finally:
            # Limpiar archivos temporales
            self._cleanup_temp_files([temp_video_path, temp_processed_path])
    
    def _get_visit_client_by_id(self, visit_client_id: int):
        """
        Obtiene el registro de cliente en visita por ID
        
        Args:
            visit_client_id: ID del cliente en visita
            
        Returns:
            ScheduledVisitClientDB: Registro de la base de datos
        """
        from app.models.db_models import ScheduledVisitClientDB
        
        db_client = self.visit_repository.session.query(ScheduledVisitClientDB).filter(
            ScheduledVisitClientDB.id == visit_client_id
        ).first()
        
        return db_client
    
    def _download_video_from_storage(self, filename: str) -> BytesIO:
        """
        Descarga un video desde Cloud Storage
        
        Args:
            filename: Nombre del archivo en el bucket
            
        Returns:
            BytesIO: Contenido del video en memoria
        """
        try:
            logger.info(f"Descargando video desde Cloud Storage: {filename}")
            
            video_content = self.cloud_storage_service.download_file(
                filename,
                self.config.BUCKET_FOLDER_VIDEOS
            )
            
            logger.info(f"Video descargado exitosamente")
            return video_content
            
        except Exception as e:
            raise Exception(f"Error al descargar video desde Cloud Storage: {str(e)}")
    
    def _process_video_with_logo(self, video_content: BytesIO, filename: str) -> Tuple[str, str]:
        """
        Procesa el video agregando el logo en los primeros 3 segundos
        
        Args:
            video_content: Contenido del video en memoria
            filename: Nombre del archivo original
            
        Returns:
            Tuple[str, str]: (ruta_video_temp, ruta_video_procesado)
        """
        try:
            logger.info(f"Procesando video: {filename}")
            
            # Crear archivos temporales
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_video:
                temp_video.write(video_content.read())
                temp_video_path = temp_video.name
            
            # Cargar el video original
            video_clip = VideoFileClip(temp_video_path)
            
            # Verificar que el logo existe
            if not os.path.exists(self.logo_path):
                raise Exception(f"Logo no encontrado en: {self.logo_path}")
            
            # Crear clip del logo (3 segundos)
            logo_duration = 3.0
            logo_clip = ImageClip(self.logo_path, duration=logo_duration)
            
            # Ajustar el tamaño del logo al tamaño del video
            logo_clip = logo_clip.resize(width=video_clip.w, height=video_clip.h)
            
            # Establecer FPS del logo igual al del video
            logo_clip = logo_clip.set_fps(video_clip.fps)
            
            # Concatenar el logo con el video original
            final_video = concatenate_videoclips([logo_clip, video_clip], method="compose")
            
            # Crear archivo temporal para el video procesado
            with tempfile.NamedTemporaryFile(suffix='_processed.mp4', delete=False) as temp_processed:
                temp_processed_path = temp_processed.name
            
            # Exportar el video procesado
            final_video.write_videofile(
                temp_processed_path,
                codec='libx264',
                audio_codec='aac',
                fps=video_clip.fps,
                logger=None  # Silenciar logs de moviepy
            )
            
            # Cerrar clips para liberar recursos
            logo_clip.close()
            video_clip.close()
            final_video.close()
            
            logger.info(f"Video procesado exitosamente")
            
            return temp_video_path, temp_processed_path
            
        except Exception as e:
            raise Exception(f"Error al procesar video: {str(e)}")
    
    def _generate_processed_filename(self, original_filename: str) -> str:
        """
        Genera el nombre del archivo procesado
        
        Args:
            original_filename: Nombre del archivo original
            
        Returns:
            str: Nombre del archivo procesado
        """
        # Obtener el nombre sin extensión
        name_without_ext = os.path.splitext(original_filename)[0]
        
        # Agregar sufijo _processed.mp4
        return f"{name_without_ext}_processed.mp4"
    
    def _upload_processed_video(self, video_path: str, filename: str) -> str:
        """
        Sube el video procesado a Cloud Storage
        
        Args:
            video_path: Ruta del video procesado en disco
            filename: Nombre del archivo en el bucket
            
        Returns:
            str: URL firmada del video subido
        """
        try:
            logger.info(f"Subiendo video procesado a Cloud Storage: {filename}")
            
            # Leer el archivo procesado
            with open(video_path, 'rb') as video_file:
                # Crear un objeto FileStorage-like para usar el método upload_file
                from werkzeug.datastructures import FileStorage
                
                file_storage = FileStorage(
                    stream=video_file,
                    filename=filename,
                    content_type='video/mp4'
                )
                
                # Subir el archivo
                success, message, signed_url = self.cloud_storage_service.upload_file(
                    file_storage,
                    filename
                )
                
                if not success:
                    raise Exception(f"Error al subir video: {message}")
                
                logger.info(f"Video procesado subido exitosamente")
                return signed_url
            
        except Exception as e:
            raise Exception(f"Error al subir video procesado: {str(e)}")
    
    def _update_visit_client_record(self, visit_client_id: int, processed_filename: str, processed_url: str):
        """
        Actualiza el registro de cliente en visita con el video procesado
        
        Args:
            visit_client_id: ID del cliente en visita
            processed_filename: Nombre del archivo procesado
            processed_url: URL del archivo procesado
        """
        try:
            logger.info(f"Actualizando registro en BD - Visit Client ID: {visit_client_id}")
            
            # Obtener el registro
            db_client = self._get_visit_client_by_id(visit_client_id)
            
            if not db_client:
                raise Exception(f"Registro no encontrado")
            
            # Actualizar campos
            db_client.filename_processed = processed_filename
            db_client.filename_url_processed = processed_url
            db_client.file_status = "Procesado"
            db_client.updated_at = datetime.utcnow()
            
            # Guardar cambios
            self.visit_repository.session.commit()
            
            logger.info(f"Registro actualizado exitosamente")
            
        except Exception as e:
            self.visit_repository.session.rollback()
            raise Exception(f"Error al actualizar registro: {str(e)}")
    
    def _cleanup_temp_files(self, file_paths: list):
        """
        Limpia archivos temporales
        
        Args:
            file_paths: Lista de rutas de archivos a eliminar
        """
        for file_path in file_paths:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.debug(f"Archivo temporal eliminado: {file_path}")
                except Exception as e:
                    logger.warning(f"Error al eliminar archivo temporal {file_path}: {str(e)}")

