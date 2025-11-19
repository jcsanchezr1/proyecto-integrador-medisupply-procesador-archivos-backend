"""
Pruebas unitarias para el repositorio base usando unittest
"""
import unittest
import sys
import os

# Agregar el directorio padre al path para importar la app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.repositories.base_repository import BaseRepository


class ConcreteRepository(BaseRepository):
    """Repositorio concreto para testing"""
    
    def __init__(self):
        self.data = {}
        self.next_id = 1
    
    def create(self, **kwargs):
        entity_id = str(self.next_id)
        self.next_id += 1
        entity = {"id": entity_id, **kwargs}
        self.data[entity_id] = entity
        return entity
    
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
            return self.data[entity_id]
        return None
    
    def delete(self, entity_id: str):
        if entity_id in self.data:
            del self.data[entity_id]
            return True
        return False
    
    def exists(self, entity_id: str):
        return entity_id in self.data


class TestBaseRepository(unittest.TestCase):
    """Pruebas para BaseRepository usando unittest"""
    
    def setUp(self):
        """Configuración antes de cada prueba"""
        self.repository = BaseRepository()
    
    def test_create_not_implemented(self):
        """Prueba que create lanza NotImplementedError"""
        with self.assertRaises(NotImplementedError):
            self.repository.create(name="Test")
    
    def test_get_by_id_not_implemented(self):
        """Prueba que get_by_id lanza NotImplementedError"""
        with self.assertRaises(NotImplementedError):
            self.repository.get_by_id("1")
    
    def test_get_all_not_implemented(self):
        """Prueba que get_all lanza NotImplementedError"""
        with self.assertRaises(NotImplementedError):
            self.repository.get_all()
    
    def test_update_not_implemented(self):
        """Prueba que update lanza NotImplementedError"""
        with self.assertRaises(NotImplementedError):
            self.repository.update("1", name="Updated")
    
    def test_delete_not_implemented(self):
        """Prueba que delete lanza NotImplementedError"""
        with self.assertRaises(NotImplementedError):
            self.repository.delete("1")
    
    def test_exists_not_implemented(self):
        """Prueba que exists lanza NotImplementedError"""
        with self.assertRaises(NotImplementedError):
            self.repository.exists("1")


class TestConcreteRepository(unittest.TestCase):
    """Pruebas para implementación concreta de BaseRepository"""
    
    def setUp(self):
        """Configuración antes de cada prueba"""
        self.repository = ConcreteRepository()
    
    def test_create(self):
        """Prueba que create funciona en implementación concreta"""
        result = self.repository.create(name="Test", status="active")
        
        self.assertIn("id", result)
        self.assertEqual(result["name"], "Test")
        self.assertEqual(result["status"], "active")
    
    def test_get_by_id(self):
        """Prueba que get_by_id funciona en implementación concreta"""
        created = self.repository.create(name="Test")
        entity_id = created["id"]
        
        result = self.repository.get_by_id(entity_id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], entity_id)
        self.assertEqual(result["name"], "Test")
    
    def test_get_by_id_not_found(self):
        """Prueba que get_by_id retorna None cuando no encuentra"""
        result = self.repository.get_by_id("999")
        
        self.assertIsNone(result)
    
    def test_get_all(self):
        """Prueba que get_all funciona en implementación concreta"""
        self.repository.create(name="Test1")
        self.repository.create(name="Test2")
        self.repository.create(name="Test3")
        
        result = self.repository.get_all()
        
        self.assertEqual(len(result), 3)
    
    def test_get_all_with_limit(self):
        """Prueba que get_all respeta el límite"""
        self.repository.create(name="Test1")
        self.repository.create(name="Test2")
        self.repository.create(name="Test3")
        
        result = self.repository.get_all(limit=2)
        
        self.assertEqual(len(result), 2)
    
    def test_get_all_with_offset(self):
        """Prueba que get_all respeta el offset"""
        self.repository.create(name="Test1")
        self.repository.create(name="Test2")
        self.repository.create(name="Test3")
        
        result = self.repository.get_all(offset=1)
        
        self.assertEqual(len(result), 2)
    
    def test_update(self):
        """Prueba que update funciona en implementación concreta"""
        created = self.repository.create(name="Test", status="active")
        entity_id = created["id"]
        
        updated = self.repository.update(entity_id, status="inactive")
        
        self.assertIsNotNone(updated)
        self.assertEqual(updated["status"], "inactive")
        self.assertEqual(updated["name"], "Test")
    
    def test_update_not_found(self):
        """Prueba que update retorna None cuando no encuentra"""
        result = self.repository.update("999", status="inactive")
        
        self.assertIsNone(result)
    
    def test_delete(self):
        """Prueba que delete funciona en implementación concreta"""
        created = self.repository.create(name="Test")
        entity_id = created["id"]
        
        result = self.repository.delete(entity_id)
        
        self.assertTrue(result)
        self.assertIsNone(self.repository.get_by_id(entity_id))
    
    def test_delete_not_found(self):
        """Prueba que delete retorna False cuando no encuentra"""
        result = self.repository.delete("999")
        
        self.assertFalse(result)
    
    def test_exists_true(self):
        """Prueba que exists retorna True cuando la entidad existe"""
        created = self.repository.create(name="Test")
        entity_id = created["id"]
        
        result = self.repository.exists(entity_id)
        
        self.assertTrue(result)
    
    def test_exists_false(self):
        """Prueba que exists retorna False cuando la entidad no existe"""
        result = self.repository.exists("999")
        
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()

