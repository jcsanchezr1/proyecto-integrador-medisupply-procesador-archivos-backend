"""
Modelo de Visita Programada
"""
from datetime import datetime, date
from typing import Optional, List
import re
import uuid
from .base_model import BaseModel


class ScheduledVisitClient:
    """Modelo para cliente asociado a visita programada"""
    
    def __init__(self, client_id: str):
        self.client_id = client_id
    
    def validate(self) -> None:
        """Valida el ID del cliente"""
        if not self.client_id:
            raise ValueError("El ID del cliente es obligatorio")
        
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if not re.match(uuid_pattern, self.client_id, re.IGNORECASE):
            raise ValueError("El client_id debe ser un UUID válido")
    
    def to_dict(self) -> dict:
        """Convierte el cliente a diccionario"""
        return {
            'client_id': self.client_id
        }


class ScheduledVisit(BaseModel):
    """Modelo de Visita Programada"""
    
    def __init__(
        self,
        seller_id: str,
        date: date,
        clients: List[ScheduledVisitClient],
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id or str(uuid.uuid4())
        self.seller_id = seller_id
        self.date = date
        self.clients = clients or []
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def validate(self) -> None:
        """Valida los datos de la visita programada"""
        self._validate_seller_id()
        self._validate_date()
        self._validate_clients()
    
    def _validate_seller_id(self) -> None:
        """Valida el ID del vendedor"""
        if not self.seller_id:
            raise ValueError("El ID del vendedor es obligatorio")
        
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if not re.match(uuid_pattern, self.seller_id, re.IGNORECASE):
            raise ValueError("El seller_id debe ser un UUID válido")
    
    def _validate_date(self) -> None:
        """Valida la fecha de la visita"""
        if not self.date:
            raise ValueError("La fecha es obligatoria")
        
        if not isinstance(self.date, date):
            raise ValueError("La fecha debe ser un objeto de tipo date")
    
    def _validate_clients(self) -> None:
        """Valida la lista de clientes"""
        if not self.clients:
            raise ValueError("Debe haber al menos un cliente en la visita")
        
        if not isinstance(self.clients, list):
            raise ValueError("Los clientes deben ser una lista")
        
        if len(self.clients) == 0:
            raise ValueError("Debe haber al menos un cliente en la visita")
        
        # Validar cada cliente
        for client in self.clients:
            if not isinstance(client, ScheduledVisitClient):
                raise ValueError("Cada cliente debe ser una instancia de ScheduledVisitClient")
            client.validate()
        
        # Validar que no haya clientes duplicados
        client_ids = [client.client_id for client in self.clients]
        if len(client_ids) != len(set(client_ids)):
            raise ValueError("No puede haber clientes duplicados en la visita")
    
    def to_dict(self) -> dict:
        """Convierte la visita programada a diccionario"""
        return {
            'id': self.id,
            'seller_id': self.seller_id,
            'date': self.date.strftime('%d-%m-%Y') if self.date else None,
            'clients': [client.to_dict() for client in self.clients],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

