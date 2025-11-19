"""
Pruebas unitarias para el modelo base usando unittest
"""
import unittest
import sys
import os

# Agregar el directorio padre al path para importar la app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models.base_model import BaseModel


class TestBaseModel(unittest.TestCase):
    """Pruebas para BaseModel usando unittest"""
    
    def test_init_with_kwargs(self):
        """Prueba que __init__ asigna correctamente los atributos"""
        model = BaseModel(id=1, name="Test", status="active")
        
        self.assertEqual(model.id, 1)
        self.assertEqual(model.name, "Test")
        self.assertEqual(model.status, "active")
    
    def test_init_empty(self):
        """Prueba que __init__ funciona sin argumentos"""
        model = BaseModel()
        
        # Verificar que el objeto se crea correctamente
        self.assertIsInstance(model, BaseModel)
    
    def test_to_dict(self):
        """Prueba que to_dict convierte correctamente el modelo a diccionario"""
        model = BaseModel(id=1, name="Test", status="active")
        result = model.to_dict()
        
        self.assertEqual(result, {
            "id": 1,
            "name": "Test",
            "status": "active"
        })
    
    def test_to_dict_excludes_private_attributes(self):
        """Prueba que to_dict excluye atributos privados"""
        model = BaseModel(id=1, name="Test")
        model._private = "secret"
        
        result = model.to_dict()
        
        self.assertIn("id", result)
        self.assertIn("name", result)
        self.assertNotIn("_private", result)
    
    def test_validate_returns_true(self):
        """Prueba que validate retorna True por defecto"""
        model = BaseModel(id=1, name="Test")
        
        self.assertTrue(model.validate())
    
    def test_repr(self):
        """Prueba que __repr__ retorna una representación correcta"""
        model = BaseModel(id=1, name="Test")
        repr_string = repr(model)
        
        self.assertIn("BaseModel", repr_string)
        self.assertIn("id", repr_string)
        self.assertIn("name", repr_string)
    
    def test_to_dict_with_nested_values(self):
        """Prueba que to_dict maneja valores anidados correctamente"""
        model = BaseModel(
            id=1,
            name="Test",
            metadata={"key": "value"},
            tags=["tag1", "tag2"]
        )
        result = model.to_dict()
        
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["name"], "Test")
        self.assertEqual(result["metadata"], {"key": "value"})
        self.assertEqual(result["tags"], ["tag1", "tag2"])


if __name__ == '__main__':
    unittest.main()

