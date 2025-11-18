"""
Repositorio para manejo de visitas programadas
"""
from typing import List, Optional, Tuple, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from datetime import date, datetime
from ..models.scheduled_visit import ScheduledVisit, ScheduledVisitClient
from ..models.db_models import ScheduledVisitDB, ScheduledVisitClientDB
from .base_repository import BaseRepository
import logging

logger = logging.getLogger(__name__)


class ScheduledVisitRepository(BaseRepository):
    """Repositorio para manejo de visitas programadas"""
    
    def __init__(self, session: Session):
        super().__init__(session)
    
    def create(self, scheduled_visit: ScheduledVisit) -> ScheduledVisit:
        """Crea una nueva visita programada"""
        logger.info(f"=== INICIANDO CREACIÓN DE VISITA PROGRAMADA: {scheduled_visit.id} ===")
        try:
            # Verificar si ya existe una visita para este vendedor en esta fecha
            existing = self.session.query(ScheduledVisitDB).filter(
                ScheduledVisitDB.seller_id == scheduled_visit.seller_id,
                ScheduledVisitDB.date == scheduled_visit.date
            ).first()
            
            if existing:
                logger.error(f"Ya existe una visita para el vendedor {scheduled_visit.seller_id} en la fecha {scheduled_visit.date}")
                raise ValueError(
                    f"Ya existe una visita programada para este vendedor en la fecha {scheduled_visit.date.strftime('%d-%m-%Y')}"
                )
            
            # Crear el registro de la visita programada
            db_visit = ScheduledVisitDB(
                id=scheduled_visit.id,
                seller_id=scheduled_visit.seller_id,
                date=scheduled_visit.date
            )
            
            self.session.add(db_visit)
            # Hacer flush para que la visita se inserte antes de los clientes
            self.session.flush()
            
            # Crear los registros de clientes asociados
            for client in scheduled_visit.clients:
                db_client = ScheduledVisitClientDB(
                    visit_id=scheduled_visit.id,
                    client_id=client.client_id,
                    status='SCHEDULED'
                )
                self.session.add(db_client)
            
            self.session.commit()
            self.session.refresh(db_visit)
            logger.info(f"Visita programada creada exitosamente con ID: {db_visit.id}")
            
            return self._db_to_model(db_visit, scheduled_visit.clients)
        except ValueError:
            # Re-lanzar errores de validación sin envolver
            raise
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error al crear visita programada: {str(e)}")
    
    def get_by_seller_with_filters(
        self,
        seller_id: str,
        visit_date: Optional[date] = None
    ) -> List[Tuple[Any, int]]:
        """Obtiene visitas programadas de un vendedor con filtros"""
        try:
            # Subconsulta para contar clientes por visita
            client_count_subquery = (
                self.session.query(
                    ScheduledVisitClientDB.visit_id,
                    func.count(ScheduledVisitClientDB.client_id).label('count_clients')
                )
                .group_by(ScheduledVisitClientDB.visit_id)
                .subquery()
            )
            
            # Consulta principal
            query = (
                self.session.query(
                    ScheduledVisitDB,
                    func.coalesce(client_count_subquery.c.count_clients, 0).label('count_clients')
                )
                .outerjoin(
                    client_count_subquery,
                    ScheduledVisitDB.id == client_count_subquery.c.visit_id
                )
                .filter(ScheduledVisitDB.seller_id == seller_id)
            )
            
            # Filtrar por fecha si se proporciona
            if visit_date:
                query = query.filter(ScheduledVisitDB.date == visit_date)
            
            # Ordenar por fecha
            query = query.order_by(ScheduledVisitDB.date)
            
            results = query.all()
            return results
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener visitas programadas: {str(e)}")
    
    def get_clients_for_visit(self, visit_id: str) -> List[ScheduledVisitClient]:
        """Obtiene los clientes asociados a una visita"""
        try:
            db_clients = (
                self.session.query(ScheduledVisitClientDB)
                .filter(ScheduledVisitClientDB.visit_id == visit_id)
                .all()
            )
            
            return [
                ScheduledVisitClient(client_id=db_client.client_id)
                for db_client in db_clients
            ]
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener clientes de la visita: {str(e)}")
    
    def get_by_id_and_seller(self, visit_id: str, seller_id: str) -> Optional[ScheduledVisit]:
        """Obtiene una visita por ID y seller_id"""
        try:
            db_visit = (
                self.session.query(ScheduledVisitDB)
                .filter(
                    ScheduledVisitDB.id == visit_id,
                    ScheduledVisitDB.seller_id == seller_id
                )
                .first()
            )
            
            if not db_visit:
                return None
            
            # Obtener los clientes asociados
            clients = self.get_clients_for_visit(visit_id)
            
            return self._db_to_model(db_visit, clients)
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener visita programada: {str(e)}")
    
    def get_client_visit(self, visit_id: str, client_id: str) -> Optional[Any]:
        """Obtiene un registro específico de cliente en una visita"""
        try:
            db_client = (
                self.session.query(ScheduledVisitClientDB)
                .filter(
                    ScheduledVisitClientDB.visit_id == visit_id,
                    ScheduledVisitClientDB.client_id == client_id
                )
                .first()
            )
            
            return db_client
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener cliente de la visita: {str(e)}")
    
    def update_client_visit(self, visit_id: str, client_id: str, update_data: dict) -> bool:
        """Actualiza un cliente de una visita"""
        try:
            db_client = self.get_client_visit(visit_id, client_id)
            
            if not db_client:
                return False
            
            # Actualizar los campos proporcionados
            for key, value in update_data.items():
                if hasattr(db_client, key):
                    setattr(db_client, key, value)
            
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error al actualizar cliente de la visita: {str(e)}")
    
    def get_all(self) -> List[ScheduledVisit]:  # pragma: no cover
        """No requerido - implementación mínima"""
        pass
    
    def get_by_id(self, entity_id: str):  # pragma: no cover
        """No requerido - implementación mínima"""
        pass
    
    def update(self, entity):  # pragma: no cover
        """No requerido - implementación mínima"""
        pass
    
    def delete(self, entity_id: str) -> bool:  # pragma: no cover
        """No requerido - implementación mínima"""
        pass
    
    def _db_to_model(self, db_visit: ScheduledVisitDB, clients: List[ScheduledVisitClient]) -> ScheduledVisit:
        """Convierte modelo de BD a modelo de dominio"""
        return ScheduledVisit(
            id=db_visit.id,
            seller_id=db_visit.seller_id,
            date=db_visit.date,
            clients=clients,
            created_at=db_visit.created_at,
            updated_at=db_visit.updated_at
        )

