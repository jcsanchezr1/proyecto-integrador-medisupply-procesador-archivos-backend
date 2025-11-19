"""
Tests adicionales para el repositorio de visitas programadas
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import date, datetime
from sqlalchemy.exc import SQLAlchemyError

from app.repositories.scheduled_visit_repository import ScheduledVisitRepository
from app.models.scheduled_visit import ScheduledVisit, ScheduledVisitClient
from app.models.db_models import ScheduledVisitDB, ScheduledVisitClientDB


@pytest.fixture
def mock_session():
    """Mock de la sesión de SQLAlchemy"""
    return Mock()


@pytest.fixture
def repository(mock_session):
    """Instancia del repositorio con sesión mock"""
    return ScheduledVisitRepository(mock_session)


class TestScheduledVisitRepositoryCreate:
    """Tests para el método create"""
    
    def test_create_success(self, repository, mock_session):
        """Test de creación exitosa"""
        # Preparar datos
        visit = ScheduledVisit(
            id="test-id",
            seller_id="123e4567-e89b-12d3-a456-426614174000",
            date=date(2024, 1, 15),
            clients=[ScheduledVisitClient("987e6543-e89b-12d3-a456-426614174000")]
        )
        
        # Configurar mocks
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_db_visit = Mock(spec=ScheduledVisitDB)
        mock_db_visit.id = visit.id
        mock_db_visit.seller_id = visit.seller_id
        mock_db_visit.date = visit.date
        mock_db_visit.created_at = datetime.utcnow()
        mock_db_visit.updated_at = datetime.utcnow()
        
        # Ejecutar
        result = repository.create(visit)
        
        # Verificar
        assert mock_session.add.called
        assert mock_session.flush.called
        assert mock_session.commit.called
        assert result.id == visit.id
    
    def test_create_duplicate_visit(self, repository, mock_session):
        """Test de creación con visita duplicada"""
        # Preparar datos
        visit = ScheduledVisit(
            seller_id="123e4567-e89b-12d3-a456-426614174000",
            date=date(2024, 1, 15),
            clients=[ScheduledVisitClient("987e6543-e89b-12d3-a456-426614174000")]
        )
        
        # Simular que ya existe una visita
        existing_visit = Mock(spec=ScheduledVisitDB)
        mock_session.query.return_value.filter.return_value.first.return_value = existing_visit
        
        # Ejecutar y verificar
        with pytest.raises(ValueError) as exc_info:
            repository.create(visit)
        
        assert "Ya existe" in str(exc_info.value)
        assert mock_session.commit.not_called
    
    def test_create_database_error(self, repository, mock_session):
        """Test de error en base de datos al crear"""
        # Preparar datos
        visit = ScheduledVisit(
            seller_id="123e4567-e89b-12d3-a456-426614174000",
            date=date(2024, 1, 15),
            clients=[ScheduledVisitClient("987e6543-e89b-12d3-a456-426614174000")]
        )
        
        # Configurar mock para lanzar excepción
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_session.commit.side_effect = SQLAlchemyError("DB Error")
        
        # Ejecutar y verificar
        with pytest.raises(Exception) as exc_info:
            repository.create(visit)
        
        assert "Error al crear visita programada" in str(exc_info.value)
        assert mock_session.rollback.called


class TestScheduledVisitRepositoryGetBySellerWithFilters:
    """Tests para el método get_by_seller_with_filters"""
    
    def test_get_by_seller_without_date_filter(self, repository, mock_session):
        """Test de obtención por vendedor sin filtro de fecha"""
        seller_id = "123e4567-e89b-12d3-a456-426614174000"
        
        # Configurar mocks
        mock_result = [(Mock(spec=ScheduledVisitDB), 2)]
        mock_session.query.return_value.outerjoin.return_value.filter.return_value.order_by.return_value.all.return_value = mock_result
        
        # Ejecutar
        result = repository.get_by_seller_with_filters(seller_id)
        
        # Verificar
        assert result == mock_result
        assert mock_session.query.called
    
    def test_get_by_seller_with_date_filter(self, repository, mock_session):
        """Test de obtención por vendedor con filtro de fecha"""
        seller_id = "123e4567-e89b-12d3-a456-426614174000"
        visit_date = date(2024, 1, 15)
        
        # Configurar mocks
        mock_query = Mock()
        mock_session.query.return_value.outerjoin.return_value.filter.return_value = mock_query
        mock_query.filter.return_value.order_by.return_value.all.return_value = []
        
        # Ejecutar
        result = repository.get_by_seller_with_filters(seller_id, visit_date=visit_date)
        
        # Verificar
        assert result == []
        assert mock_query.filter.called  # Filtro de fecha aplicado
    
    def test_get_by_seller_database_error(self, repository, mock_session):
        """Test de error en base de datos"""
        seller_id = "123e4567-e89b-12d3-a456-426614174000"
        
        # Configurar mock para lanzar excepción
        mock_session.query.side_effect = SQLAlchemyError("DB Error")
        
        # Ejecutar y verificar
        with pytest.raises(Exception) as exc_info:
            repository.get_by_seller_with_filters(seller_id)
        
        assert "Error al obtener visitas programadas" in str(exc_info.value)


class TestScheduledVisitRepositoryGetClientsForVisit:
    """Tests para el método get_clients_for_visit"""
    
    def test_get_clients_success(self, repository, mock_session):
        """Test de obtención exitosa de clientes"""
        visit_id = "test-visit-id"
        
        # Configurar mocks
        mock_client1 = Mock(spec=ScheduledVisitClientDB)
        mock_client1.client_id = "123e4567-e89b-12d3-a456-426614174000"
        mock_client2 = Mock(spec=ScheduledVisitClientDB)
        mock_client2.client_id = "987e6543-e89b-12d3-a456-426614174000"
        
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_client1, mock_client2]
        
        # Ejecutar
        result = repository.get_clients_for_visit(visit_id)
        
        # Verificar
        assert len(result) == 2
        assert all(isinstance(client, ScheduledVisitClient) for client in result)
        assert result[0].client_id == mock_client1.client_id
        assert result[1].client_id == mock_client2.client_id
    
    def test_get_clients_empty(self, repository, mock_session):
        """Test con visita sin clientes"""
        visit_id = "test-visit-id"
        
        # Configurar mock para devolver lista vacía
        mock_session.query.return_value.filter.return_value.all.return_value = []
        
        # Ejecutar
        result = repository.get_clients_for_visit(visit_id)
        
        # Verificar
        assert result == []
    
    def test_get_clients_database_error(self, repository, mock_session):
        """Test de error en base de datos"""
        visit_id = "test-visit-id"
        
        # Configurar mock para lanzar excepción
        mock_session.query.side_effect = SQLAlchemyError("DB Error")
        
        # Ejecutar y verificar
        with pytest.raises(Exception) as exc_info:
            repository.get_clients_for_visit(visit_id)
        
        assert "Error al obtener clientes" in str(exc_info.value)


class TestScheduledVisitRepositoryGetByIdAndSeller:
    """Tests para el método get_by_id_and_seller"""
    
    def test_get_by_id_and_seller_found(self, repository, mock_session):
        """Test de obtención exitosa por ID y vendedor"""
        visit_id = "test-visit-id"
        seller_id = "123e4567-e89b-12d3-a456-426614174000"
        
        # Configurar mocks
        mock_db_visit = Mock(spec=ScheduledVisitDB)
        mock_db_visit.id = visit_id
        mock_db_visit.seller_id = seller_id
        mock_db_visit.date = date(2024, 1, 15)
        mock_db_visit.created_at = datetime.utcnow()
        mock_db_visit.updated_at = datetime.utcnow()
        
        mock_session.query.return_value.filter.return_value.first.return_value = mock_db_visit
        
        # Mock para get_clients_for_visit
        with patch.object(repository, 'get_clients_for_visit') as mock_get_clients:
            mock_get_clients.return_value = [ScheduledVisitClient("987e6543-e89b-12d3-a456-426614174000")]
            
            # Ejecutar
            result = repository.get_by_id_and_seller(visit_id, seller_id)
            
            # Verificar
            assert result is not None
            assert result.id == visit_id
            assert result.seller_id == seller_id
            assert mock_get_clients.called_with(visit_id)
    
    def test_get_by_id_and_seller_not_found(self, repository, mock_session):
        """Test con visita no encontrada"""
        visit_id = "nonexistent-id"
        seller_id = "123e4567-e89b-12d3-a456-426614174000"
        
        # Configurar mock para devolver None
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        # Ejecutar
        result = repository.get_by_id_and_seller(visit_id, seller_id)
        
        # Verificar
        assert result is None
    
    def test_get_by_id_and_seller_database_error(self, repository, mock_session):
        """Test de error en base de datos"""
        visit_id = "test-visit-id"
        seller_id = "123e4567-e89b-12d3-a456-426614174000"
        
        # Configurar mock para lanzar excepción
        mock_session.query.side_effect = SQLAlchemyError("DB Error")
        
        # Ejecutar y verificar
        with pytest.raises(Exception) as exc_info:
            repository.get_by_id_and_seller(visit_id, seller_id)
        
        assert "Error al obtener visita programada" in str(exc_info.value)


class TestScheduledVisitRepositoryGetClientVisit:
    """Tests para el método get_client_visit"""
    
    def test_get_client_visit_found(self, repository, mock_session):
        """Test de obtención exitosa de cliente en visita"""
        visit_id = "test-visit-id"
        client_id = "123e4567-e89b-12d3-a456-426614174000"
        
        # Configurar mock
        mock_db_client = Mock(spec=ScheduledVisitClientDB)
        mock_session.query.return_value.filter.return_value.first.return_value = mock_db_client
        
        # Ejecutar
        result = repository.get_client_visit(visit_id, client_id)
        
        # Verificar
        assert result == mock_db_client
    
    def test_get_client_visit_not_found(self, repository, mock_session):
        """Test con cliente no encontrado"""
        visit_id = "test-visit-id"
        client_id = "123e4567-e89b-12d3-a456-426614174000"
        
        # Configurar mock para devolver None
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        # Ejecutar
        result = repository.get_client_visit(visit_id, client_id)
        
        # Verificar
        assert result is None
    
    def test_get_client_visit_database_error(self, repository, mock_session):
        """Test de error en base de datos"""
        visit_id = "test-visit-id"
        client_id = "123e4567-e89b-12d3-a456-426614174000"
        
        # Configurar mock para lanzar excepción
        mock_session.query.side_effect = SQLAlchemyError("DB Error")
        
        # Ejecutar y verificar
        with pytest.raises(Exception) as exc_info:
            repository.get_client_visit(visit_id, client_id)
        
        assert "Error al obtener cliente de la visita" in str(exc_info.value)


class TestScheduledVisitRepositoryUpdateClientVisit:
    """Tests para el método update_client_visit"""
    
    def test_update_client_visit_success(self, repository, mock_session):
        """Test de actualización exitosa"""
        visit_id = "test-visit-id"
        client_id = "123e4567-e89b-12d3-a456-426614174000"
        update_data = {'status': 'COMPLETED', 'find': 'Visita exitosa'}
        
        # Configurar mock
        mock_db_client = Mock(spec=ScheduledVisitClientDB)
        mock_db_client.status = 'SCHEDULED'
        
        with patch.object(repository, 'get_client_visit') as mock_get_client:
            mock_get_client.return_value = mock_db_client
            
            # Ejecutar
            result = repository.update_client_visit(visit_id, client_id, update_data)
            
            # Verificar
            assert result is True
            assert mock_db_client.status == 'COMPLETED'
            assert mock_db_client.find == 'Visita exitosa'
            assert mock_session.commit.called
    
    def test_update_client_visit_not_found(self, repository, mock_session):
        """Test de actualización con cliente no encontrado"""
        visit_id = "test-visit-id"
        client_id = "123e4567-e89b-12d3-a456-426614174000"
        update_data = {'status': 'COMPLETED'}
        
        # Configurar mock para devolver None
        with patch.object(repository, 'get_client_visit') as mock_get_client:
            mock_get_client.return_value = None
            
            # Ejecutar
            result = repository.update_client_visit(visit_id, client_id, update_data)
            
            # Verificar
            assert result is False
            assert not mock_session.commit.called
    
    def test_update_client_visit_database_error(self, repository, mock_session):
        """Test de error en base de datos"""
        visit_id = "test-visit-id"
        client_id = "123e4567-e89b-12d3-a456-426614174000"
        update_data = {'status': 'COMPLETED'}
        
        # Configurar mock
        mock_db_client = Mock(spec=ScheduledVisitClientDB)
        
        with patch.object(repository, 'get_client_visit') as mock_get_client:
            mock_get_client.return_value = mock_db_client
            mock_session.commit.side_effect = SQLAlchemyError("DB Error")
            
            # Ejecutar y verificar
            with pytest.raises(Exception) as exc_info:
                repository.update_client_visit(visit_id, client_id, update_data)
            
            assert "Error al actualizar cliente" in str(exc_info.value)
            assert mock_session.rollback.called


class TestScheduledVisitRepositoryDbToModel:
    """Tests para el método _db_to_model"""
    
    def test_db_to_model_conversion(self, repository):
        """Test de conversión de BD a modelo"""
        # Preparar mock de BD
        mock_db_visit = Mock(spec=ScheduledVisitDB)
        mock_db_visit.id = "test-id"
        mock_db_visit.seller_id = "123e4567-e89b-12d3-a456-426614174000"
        mock_db_visit.date = date(2024, 1, 15)
        mock_db_visit.created_at = datetime(2024, 1, 1, 10, 0, 0)
        mock_db_visit.updated_at = datetime(2024, 1, 2, 11, 0, 0)
        
        # Preparar clientes
        clients = [ScheduledVisitClient("987e6543-e89b-12d3-a456-426614174000")]
        
        # Ejecutar
        result = repository._db_to_model(mock_db_visit, clients)
        
        # Verificar
        assert isinstance(result, ScheduledVisit)
        assert result.id == mock_db_visit.id
        assert result.seller_id == mock_db_visit.seller_id
        assert result.date == mock_db_visit.date
        assert len(result.clients) == 1
        assert result.created_at == mock_db_visit.created_at
        assert result.updated_at == mock_db_visit.updated_at

