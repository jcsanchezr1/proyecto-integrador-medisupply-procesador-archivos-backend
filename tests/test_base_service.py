"""
Pruebas unitarias para el servicio base usando unittest
"""
import unittest
import sys
import os

# Agregar el directorio padre al path para importar la app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.base_service import BaseService


class ConcreteService(BaseService):
    """Servicio concreto para testing"""
    
    def __init__(self):
        self.data = {}
        self.next_id = 1
    
    def create(self, **kwargs):
        entity_id = str(self.next_id)
        self.next_id += 1
        self.data[entity_id] = kwargs
        return {"id": entity_id, **kwargs}
    
    def get_by_id(self, entity_id: str):
        return self.data.get(entity_id)
    
    def get_all(self, limit=None, offset=0):
        items = list(self.data.values())
        if limit:
            return items[offset:offset + limit]
        return items[offset:]
    
    def update(self, entity_id: str, **kwargs):
        if entity_id in self.data:
            self.data[entity_id].update(kwargs)
            return {"id": entity_id, **self.data[entity_id]}
        return None
    
    def delete(self, entity_id: str):
        if entity_id in self.data:
            del self.data[entity_id]
            return True
        return False


class TestBaseService(unittest.TestCase):
    """Pruebas para BaseService usando unittest"""
    
    def setUp(self):
        """Configuración antes de cada prueba"""
        self.service = BaseService()
    
    def test_validate_business_rules_exists(self):
        """Prueba que validate_business_rules existe y es callable"""
        self.assertTrue(hasattr(self.service, 'validate_business_rules'))
        self.assertTrue(callable(self.service.validate_business_rules))
    
    def test_validate_business_rules_does_nothing_by_default(self):
        """Prueba que validate_business_rules no hace nada por defecto"""
        # No debe lanzar excepción
        result = self.service.validate_business_rules(test="value")
        self.assertIsNone(result)
    
    def test_create_not_implemented(self):
        """Prueba que create lanza NotImplementedError"""
        with self.assertRaises(NotImplementedError):
            self.service.create(name="Test")
    
    def test_get_by_id_not_implemented(self):
        """Prueba que get_by_id lanza NotImplementedError"""
        with self.assertRaises(NotImplementedError):
            self.service.get_by_id("1")
    
    def test_get_all_not_implemented(self):
        """Prueba que get_all lanza NotImplementedError"""
        with self.assertRaises(NotImplementedError):
            self.service.get_all()
    
    def test_update_not_implemented(self):
        """Prueba que update lanza NotImplementedError"""
        with self.assertRaises(NotImplementedError):
            self.service.update("1", name="Updated")
    
    def test_delete_not_implemented(self):
        """Prueba que delete lanza NotImplementedError"""
        with self.assertRaises(NotImplementedError):
            self.service.delete("1")


class TestConcreteService(unittest.TestCase):
    """Pruebas para implementación concreta de BaseService"""
    
    def setUp(self):
        """Configuración antes de cada prueba"""
        self.service = ConcreteService()
    
    def test_create(self):
        """Prueba que create funciona en implementación concreta"""
        result = self.service.create(name="Test", status="active")
        
        self.assertIn("id", result)
        self.assertEqual(result["name"], "Test")
        self.assertEqual(result["status"], "active")
    
    def test_get_by_id(self):
        """Prueba que get_by_id funciona en implementación concreta"""
        created = self.service.create(name="Test")
        entity_id = created["id"]
        
        result = self.service.get_by_id(entity_id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Test")
    
    def test_get_all(self):
        """Prueba que get_all funciona en implementación concreta"""
        self.service.create(name="Test1")
        self.service.create(name="Test2")
        
        result = self.service.get_all()
        
        self.assertEqual(len(result), 2)
    
    def test_update(self):
        """Prueba que update funciona en implementación concreta"""
        created = self.service.create(name="Test", status="active")
        entity_id = created["id"]
        
        updated = self.service.update(entity_id, status="inactive")
        
        self.assertEqual(updated["status"], "inactive")
    
    def test_delete(self):
        """Prueba que delete funciona en implementación concreta"""
        created = self.service.create(name="Test")
        entity_id = created["id"]
        
        result = self.service.delete(entity_id)
        
        self.assertTrue(result)
        self.assertIsNone(self.service.get_by_id(entity_id))


if __name__ == '__main__':
    unittest.main()

