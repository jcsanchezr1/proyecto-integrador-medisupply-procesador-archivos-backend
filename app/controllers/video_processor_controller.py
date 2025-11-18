"""
Controlador para procesar videos de visitas desde eventos de Pub/Sub
"""
import logging
import json
import base64
from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.controllers.base_controller import BaseController
from app.services.video_processor_service import VideoProcessorService
from app.repositories.scheduled_visit_repository import ScheduledVisitRepository
from app.config.settings import Config

logger = logging.getLogger(__name__)

# Crear Blueprint para el controlador
video_processor_bp = Blueprint('video_processor', __name__, url_prefix='/files-procesor')


class VideoProcessorController(BaseController):
    """
    Controlador para procesar videos de visitas desde Cloud Storage
    """
    
    def __init__(self, processor_service=None):
        if processor_service:
            self.processor_service = processor_service
        else:
            # Crear sesión de BD y repositorio
            config = Config()
            engine = create_engine(config.DATABASE_URL)
            Session = sessionmaker(bind=engine)
            session = Session()
            
            # Crear repositorio y servicio
            visit_repository = ScheduledVisitRepository(session)
            self.processor_service = VideoProcessorService(
                visit_repository=visit_repository,
                config=config
            )
    
    def process_video(self):
        """
        Endpoint POST para procesar videos desde eventos Pub/Sub push
        
        Recibe un evento de Pub/Sub con el formato:
        {
            "message": {
                "data": "base64_encoded_data",
                "messageId": "message_id",
                "publishTime": "timestamp"
            },
            "subscription": "subscription_name"
        }
        
        El data decodificado contiene:
        {
            "scheduled_visit_client_id": 1234,
            "event_type": "video_processing",
            "timestamp": "2024-01-15T10:30:00.000000"
        }
        
        Returns:
            Response: Respuesta HTTP con resultado del procesamiento
        """
        try:
            # Validar que la petición tenga contenido
            try:
                pubsub_message = request.get_json(force=True)
                if not pubsub_message:
                    logger.warning("Petición sin contenido JSON")
                    return jsonify({
                        "success": False,
                        "message": "Petición sin contenido JSON"
                    }), 400
            except Exception:
                logger.warning("Petición sin contenido JSON válido")
                return jsonify({
                    "success": False,
                    "message": "Petición sin contenido JSON"
                }), 400
            
            if 'message' not in pubsub_message:
                logger.warning("Mensaje de Pub/Sub sin campo 'message'")
                return jsonify({
                    "success": False,
                    "message": "Formato de mensaje Pub/Sub inválido"
                }), 400
            
            message = pubsub_message['message']
            
            # Decodificar el data del mensaje
            if 'data' not in message:
                logger.warning("Mensaje de Pub/Sub sin campo 'data'")
                return jsonify({
                    "success": False,
                    "message": "Mensaje sin data"
                }), 400
            
            # Decodificar base64
            try:
                data_decoded = base64.b64decode(message['data']).decode('utf-8')
                event_data = json.loads(data_decoded)
            except Exception as e:
                logger.error(f"Error al decodificar mensaje: {str(e)}")
                return jsonify({
                    "success": False,
                    "message": f"Error al decodificar mensaje: {str(e)}"
                }), 400
            
            # Extraer scheduled_visit_client_id del evento
            scheduled_visit_client_id = event_data.get('scheduled_visit_client_id')
            if not scheduled_visit_client_id:
                logger.warning("Evento sin scheduled_visit_client_id")
                return jsonify({
                    "success": False,
                    "message": "Evento sin scheduled_visit_client_id"
                }), 400
            
            # Convertir a entero
            try:
                scheduled_visit_client_id = int(scheduled_visit_client_id)
            except ValueError:
                logger.warning(f"scheduled_visit_client_id inválido: {scheduled_visit_client_id}")
                return jsonify({
                    "success": False,
                    "message": "scheduled_visit_client_id debe ser un número entero"
                }), 400
            
            logger.info(f"Procesando video - Scheduled Visit Client ID: {scheduled_visit_client_id}, Event Type: {event_data.get('event_type')}")
            
            # Procesar el video
            result = self.processor_service.process_video_by_visit_client_id(scheduled_visit_client_id)
            
            logger.info(f"Video procesado exitosamente - {result['processed_filename']}")
            
            return jsonify({
                "success": True,
                "message": "Video procesado exitosamente",
                "data": result
            }), 200
            
        except Exception as e:
            logger.error(f"Error al procesar video: {str(e)}")
            return jsonify({
                "success": False,
                "message": f"Error al procesar video: {str(e)}"
            }), 500


# Registrar las rutas
@video_processor_bp.route('/video', methods=['POST'])
def process_video():
    """
    Endpoint POST /files-procesor/video
    
    Procesa videos desde eventos Pub/Sub push
    """
    controller = VideoProcessorController()
    return controller.process_video()

