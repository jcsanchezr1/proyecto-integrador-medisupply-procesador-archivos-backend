"""
Tests para el modelo de Visita Programada
"""
import pytest
from datetime import date, datetime
from app.models.scheduled_visit import ScheduledVisit, ScheduledVisitClient


class TestScheduledVisitClient:
    """Tests para ScheduledVisitClient"""
    
    def test_client_initialization(self):
        """Test de inicialización de cliente"""
        client_id = "123e4567-e89b-12d3-a456-426614174000"
        client = ScheduledVisitClient(client_id=client_id)
        
        assert client.client_id == client_id
    
    def test_client_validate_success(self):
        """Test de validación exitosa de cliente"""
        client_id = "123e4567-e89b-12d3-a456-426614174000"
        client = ScheduledVisitClient(client_id=client_id)
        
        # No debe lanzar excepción
        client.validate()
    
    def test_client_validate_empty_id(self):
        """Test de validación con ID vacío"""
        client = ScheduledVisitClient(client_id="")
        
        with pytest.raises(ValueError) as exc_info:
            client.validate()
        
        assert "obligatorio" in str(exc_info.value)
    
    def test_client_validate_none_id(self):
        """Test de validación con ID None"""
        client = ScheduledVisitClient(client_id=None)
        
        with pytest.raises(ValueError) as exc_info:
            client.validate()
        
        assert "obligatorio" in str(exc_info.value)
    
    def test_client_validate_invalid_uuid(self):
        """Test de validación con UUID inválido"""
        client = ScheduledVisitClient(client_id="invalid-uuid")
        
        with pytest.raises(ValueError) as exc_info:
            client.validate()
        
        assert "UUID válido" in str(exc_info.value)
    
    def test_client_validate_uuid_case_insensitive(self):
        """Test de validación con UUID en mayúsculas"""
        client_id = "123E4567-E89B-12D3-A456-426614174000"
        client = ScheduledVisitClient(client_id=client_id)
        
        # No debe lanzar excepción
        client.validate()
    
    def test_client_to_dict(self):
        """Test de conversión a diccionario"""
        client_id = "123e4567-e89b-12d3-a456-426614174000"
        client = ScheduledVisitClient(client_id=client_id)
        
        result = client.to_dict()
        
        assert result == {'client_id': client_id}
        assert isinstance(result, dict)


class TestScheduledVisit:
    """Tests para ScheduledVisit"""
    
    def test_visit_initialization_with_defaults(self):
        """Test de inicialización con valores por defecto"""
        seller_id = "123e4567-e89b-12d3-a456-426614174000"
        visit_date = date(2024, 1, 15)
        client = ScheduledVisitClient("987e6543-e89b-12d3-a456-426614174000")
        
        visit = ScheduledVisit(
            seller_id=seller_id,
            date=visit_date,
            clients=[client]
        )
        
        assert visit.seller_id == seller_id
        assert visit.date == visit_date
        assert len(visit.clients) == 1
        assert visit.id is not None
        assert visit.created_at is not None
        assert visit.updated_at is not None
    
    def test_visit_initialization_with_id(self):
        """Test de inicialización con ID específico"""
        visit_id = "111e1111-e11b-11d3-a111-111111111111"
        seller_id = "123e4567-e89b-12d3-a456-426614174000"
        visit_date = date(2024, 1, 15)
        client = ScheduledVisitClient("987e6543-e89b-12d3-a456-426614174000")
        
        visit = ScheduledVisit(
            id=visit_id,
            seller_id=seller_id,
            date=visit_date,
            clients=[client]
        )
        
        assert visit.id == visit_id
    
    def test_visit_initialization_with_timestamps(self):
        """Test de inicialización con timestamps específicos"""
        seller_id = "123e4567-e89b-12d3-a456-426614174000"
        visit_date = date(2024, 1, 15)
        client = ScheduledVisitClient("987e6543-e89b-12d3-a456-426614174000")
        created = datetime(2024, 1, 1, 10, 0, 0)
        updated = datetime(2024, 1, 2, 11, 0, 0)
        
        visit = ScheduledVisit(
            seller_id=seller_id,
            date=visit_date,
            clients=[client],
            created_at=created,
            updated_at=updated
        )
        
        assert visit.created_at == created
        assert visit.updated_at == updated
    
    def test_visit_validate_success(self):
        """Test de validación exitosa"""
        seller_id = "123e4567-e89b-12d3-a456-426614174000"
        visit_date = date(2024, 1, 15)
        client = ScheduledVisitClient("987e6543-e89b-12d3-a456-426614174000")
        
        visit = ScheduledVisit(
            seller_id=seller_id,
            date=visit_date,
            clients=[client]
        )
        
        # No debe lanzar excepción
        visit.validate()
    
    def test_visit_validate_empty_seller_id(self):
        """Test de validación con seller_id vacío"""
        visit_date = date(2024, 1, 15)
        client = ScheduledVisitClient("987e6543-e89b-12d3-a456-426614174000")
        
        visit = ScheduledVisit(
            seller_id="",
            date=visit_date,
            clients=[client]
        )
        
        with pytest.raises(ValueError) as exc_info:
            visit.validate()
        
        assert "vendedor" in str(exc_info.value).lower()
    
    def test_visit_validate_none_seller_id(self):
        """Test de validación con seller_id None"""
        visit_date = date(2024, 1, 15)
        client = ScheduledVisitClient("987e6543-e89b-12d3-a456-426614174000")
        
        visit = ScheduledVisit(
            seller_id=None,
            date=visit_date,
            clients=[client]
        )
        
        with pytest.raises(ValueError) as exc_info:
            visit.validate()
        
        assert "vendedor" in str(exc_info.value).lower()
    
    def test_visit_validate_invalid_seller_uuid(self):
        """Test de validación con seller_id UUID inválido"""
        visit_date = date(2024, 1, 15)
        client = ScheduledVisitClient("987e6543-e89b-12d3-a456-426614174000")
        
        visit = ScheduledVisit(
            seller_id="invalid-uuid",
            date=visit_date,
            clients=[client]
        )
        
        with pytest.raises(ValueError) as exc_info:
            visit.validate()
        
        assert "UUID válido" in str(exc_info.value)
    
    def test_visit_validate_none_date(self):
        """Test de validación con fecha None"""
        seller_id = "123e4567-e89b-12d3-a456-426614174000"
        client = ScheduledVisitClient("987e6543-e89b-12d3-a456-426614174000")
        
        visit = ScheduledVisit(
            seller_id=seller_id,
            date=None,
            clients=[client]
        )
        
        with pytest.raises(ValueError) as exc_info:
            visit.validate()
        
        assert "fecha" in str(exc_info.value).lower()
    
    def test_visit_validate_invalid_date_type(self):
        """Test de validación con tipo de fecha inválido"""
        seller_id = "123e4567-e89b-12d3-a456-426614174000"
        client = ScheduledVisitClient("987e6543-e89b-12d3-a456-426614174000")
        
        visit = ScheduledVisit(
            seller_id=seller_id,
            date="2024-01-15",  # String en lugar de date
            clients=[client]
        )
        
        with pytest.raises(ValueError) as exc_info:
            visit.validate()
        
        assert "objeto de tipo date" in str(exc_info.value)
    
    def test_visit_validate_empty_clients_list(self):
        """Test de validación con lista de clientes vacía"""
        seller_id = "123e4567-e89b-12d3-a456-426614174000"
        visit_date = date(2024, 1, 15)
        
        visit = ScheduledVisit(
            seller_id=seller_id,
            date=visit_date,
            clients=[]
        )
        
        with pytest.raises(ValueError) as exc_info:
            visit.validate()
        
        assert "al menos un cliente" in str(exc_info.value)
    
    def test_visit_validate_none_clients(self):
        """Test de validación con clientes None"""
        seller_id = "123e4567-e89b-12d3-a456-426614174000"
        visit_date = date(2024, 1, 15)
        
        visit = ScheduledVisit(
            seller_id=seller_id,
            date=visit_date,
            clients=None
        )
        
        with pytest.raises(ValueError) as exc_info:
            visit.validate()
        
        assert "al menos un cliente" in str(exc_info.value)
    
    def test_visit_validate_clients_not_list(self):
        """Test de validación con clientes que no es lista"""
        seller_id = "123e4567-e89b-12d3-a456-426614174000"
        visit_date = date(2024, 1, 15)
        
        visit = ScheduledVisit(
            seller_id=seller_id,
            date=visit_date,
            clients="not-a-list"
        )
        
        with pytest.raises(ValueError) as exc_info:
            visit.validate()
        
        assert "lista" in str(exc_info.value)
    
    def test_visit_validate_invalid_client_type(self):
        """Test de validación con tipo de cliente inválido"""
        seller_id = "123e4567-e89b-12d3-a456-426614174000"
        visit_date = date(2024, 1, 15)
        
        visit = ScheduledVisit(
            seller_id=seller_id,
            date=visit_date,
            clients=["not-a-client-object"]
        )
        
        with pytest.raises(ValueError) as exc_info:
            visit.validate()
        
        assert "ScheduledVisitClient" in str(exc_info.value)
    
    def test_visit_validate_duplicate_clients(self):
        """Test de validación con clientes duplicados"""
        seller_id = "123e4567-e89b-12d3-a456-426614174000"
        visit_date = date(2024, 1, 15)
        client_id = "987e6543-e89b-12d3-a456-426614174000"
        
        visit = ScheduledVisit(
            seller_id=seller_id,
            date=visit_date,
            clients=[
                ScheduledVisitClient(client_id),
                ScheduledVisitClient(client_id)  # Duplicado
            ]
        )
        
        with pytest.raises(ValueError) as exc_info:
            visit.validate()
        
        assert "duplicados" in str(exc_info.value)
    
    def test_visit_validate_multiple_clients(self):
        """Test de validación con múltiples clientes válidos"""
        seller_id = "123e4567-e89b-12d3-a456-426614174000"
        visit_date = date(2024, 1, 15)
        
        visit = ScheduledVisit(
            seller_id=seller_id,
            date=visit_date,
            clients=[
                ScheduledVisitClient("987e6543-e89b-12d3-a456-426614174000"),
                ScheduledVisitClient("111e1111-e11b-11d3-a111-111111111111"),
                ScheduledVisitClient("222e2222-e22b-22d3-a222-222222222222")
            ]
        )
        
        # No debe lanzar excepción
        visit.validate()
    
    def test_visit_to_dict(self):
        """Test de conversión a diccionario"""
        visit_id = "111e1111-e11b-11d3-a111-111111111111"
        seller_id = "123e4567-e89b-12d3-a456-426614174000"
        visit_date = date(2024, 1, 15)
        client_id = "987e6543-e89b-12d3-a456-426614174000"
        created = datetime(2024, 1, 1, 10, 0, 0)
        updated = datetime(2024, 1, 2, 11, 0, 0)
        
        visit = ScheduledVisit(
            id=visit_id,
            seller_id=seller_id,
            date=visit_date,
            clients=[ScheduledVisitClient(client_id)],
            created_at=created,
            updated_at=updated
        )
        
        result = visit.to_dict()
        
        assert result['id'] == visit_id
        assert result['seller_id'] == seller_id
        assert result['date'] == '15-01-2024'
        assert len(result['clients']) == 1
        assert result['clients'][0]['client_id'] == client_id
        assert result['created_at'] == created.isoformat()
        assert result['updated_at'] == updated.isoformat()
    
    def test_visit_to_dict_none_date(self):
        """Test de conversión a diccionario con fecha None"""
        seller_id = "123e4567-e89b-12d3-a456-426614174000"
        client = ScheduledVisitClient("987e6543-e89b-12d3-a456-426614174000")
        
        visit = ScheduledVisit(
            seller_id=seller_id,
            date=None,
            clients=[client]
        )
        
        result = visit.to_dict()
        
        assert result['date'] is None
    
    def test_visit_to_dict_none_timestamps(self):
        """Test de conversión a diccionario con timestamps None - se asignan automáticamente"""
        seller_id = "123e4567-e89b-12d3-a456-426614174000"
        visit_date = date(2024, 1, 15)
        client = ScheduledVisitClient("987e6543-e89b-12d3-a456-426614174000")
        
        visit = ScheduledVisit(
            seller_id=seller_id,
            date=visit_date,
            clients=[client],
            created_at=None,
            updated_at=None
        )
        
        result = visit.to_dict()
        
        # Los timestamps se asignan automáticamente si son None
        assert result['created_at'] is not None
        assert result['updated_at'] is not None

