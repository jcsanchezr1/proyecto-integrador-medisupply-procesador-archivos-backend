"""
Pruebas unitarias para el controlador base usando unittest
"""
import unittest
import sys
import os

# Agregar el directorio padre al path para importar la app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.controllers.base_controller import BaseController


class TestBaseController(unittest.TestCase):
    """Pruebas para BaseController usando unittest"""
    
    def setUp(self):
        """Configuración antes de cada prueba"""
        self.controller = BaseController()
    
    def test_success_response_with_data(self):
        """Prueba que success_response retorna correctamente con datos"""
        data = {"id": 1, "name": "Test"}
        result, status_code = self.controller.success_response(
            data=data,
            message="Operación exitosa"
        )
        
        self.assertEqual(status_code, 200)
        self.assertEqual(result["message"], "Operación exitosa")
        self.assertEqual(result["data"], data)
    
    def test_success_response_without_data(self):
        """Prueba que success_response retorna correctamente sin datos"""
        result, status_code = self.controller.success_response(
            message="Operación exitosa"
        )
        
        self.assertEqual(status_code, 200)
        self.assertEqual(result["message"], "Operación exitosa")
        self.assertNotIn("data", result)
    
    def test_success_response_custom_status_code(self):
        """Prueba que success_response acepta código de estado personalizado"""
        result, status_code = self.controller.success_response(
            message="Creado",
            status_code=201
        )
        
        self.assertEqual(status_code, 201)
        self.assertEqual(result["message"], "Creado")
    
    def test_error_response_default_status_code(self):
        """Prueba que error_response retorna correctamente con código por defecto"""
        result, status_code = self.controller.error_response(
            message="Error en la operación"
        )
        
        self.assertEqual(status_code, 400)
        self.assertEqual(result["error"], "Error en la operación")
    
    def test_error_response_custom_status_code(self):
        """Prueba que error_response acepta código de estado personalizado"""
        result, status_code = self.controller.error_response(
            message="No encontrado",
            status_code=404
        )
        
        self.assertEqual(status_code, 404)
        self.assertEqual(result["error"], "No encontrado")
    
    def test_handle_exception(self):
        """Prueba que handle_exception maneja excepciones correctamente"""
        exception = ValueError("Error de prueba")
        result, status_code = self.controller.handle_exception(exception)
        
        self.assertEqual(status_code, 500)
        self.assertEqual(result["error"], "Error de prueba")
    
    def test_base_controller_is_resource(self):
        """Prueba que BaseController hereda de Resource"""
        from flask_restful import Resource
        self.assertIsInstance(self.controller, Resource)


if __name__ == '__main__':
    unittest.main()

