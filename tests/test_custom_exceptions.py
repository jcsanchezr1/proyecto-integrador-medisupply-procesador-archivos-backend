"""
Pruebas unitarias para las excepciones personalizadas usando unittest
"""
import unittest
import sys
import os

# Agregar el directorio padre al path para importar la app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.exceptions.custom_exceptions import ValidationError, DatabaseError, ServiceError


class TestValidationError(unittest.TestCase):
    """Pruebas para ValidationError"""
    
    def test_validation_error_is_exception(self):
        """Prueba que ValidationError hereda de Exception"""
        self.assertTrue(issubclass(ValidationError, Exception))
    
    def test_validation_error_can_be_raised(self):
        """Prueba que ValidationError puede ser lanzada"""
        with self.assertRaises(ValidationError):
            raise ValidationError("Error de validación")
    
    def test_validation_error_with_message(self):
        """Prueba que ValidationError puede llevar un mensaje"""
        message = "Campo requerido faltante"
        try:
            raise ValidationError(message)
        except ValidationError as e:
            self.assertEqual(str(e), message)
    
    def test_validation_error_without_message(self):
        """Prueba que ValidationError puede ser lanzada sin mensaje"""
        try:
            raise ValidationError()
        except ValidationError as e:
            self.assertEqual(str(e), "")
    
    def test_validation_error_can_be_caught_as_exception(self):
        """Prueba que ValidationError puede ser capturada como Exception"""
        with self.assertRaises(Exception):
            raise ValidationError("Error")
    
    def test_validation_error_instance(self):
        """Prueba que se puede crear una instancia de ValidationError"""
        error = ValidationError("Test error")
        self.assertIsInstance(error, ValidationError)
        self.assertIsInstance(error, Exception)


class TestDatabaseError(unittest.TestCase):
    """Pruebas para DatabaseError"""
    
    def test_database_error_is_exception(self):
        """Prueba que DatabaseError hereda de Exception"""
        self.assertTrue(issubclass(DatabaseError, Exception))
    
    def test_database_error_can_be_raised(self):
        """Prueba que DatabaseError puede ser lanzada"""
        with self.assertRaises(DatabaseError):
            raise DatabaseError("Error de base de datos")
    
    def test_database_error_with_message(self):
        """Prueba que DatabaseError puede llevar un mensaje"""
        message = "Conexión a la base de datos fallida"
        try:
            raise DatabaseError(message)
        except DatabaseError as e:
            self.assertEqual(str(e), message)
    
    def test_database_error_without_message(self):
        """Prueba que DatabaseError puede ser lanzada sin mensaje"""
        try:
            raise DatabaseError()
        except DatabaseError as e:
            self.assertEqual(str(e), "")
    
    def test_database_error_can_be_caught_as_exception(self):
        """Prueba que DatabaseError puede ser capturada como Exception"""
        with self.assertRaises(Exception):
            raise DatabaseError("Error")
    
    def test_database_error_instance(self):
        """Prueba que se puede crear una instancia de DatabaseError"""
        error = DatabaseError("Connection timeout")
        self.assertIsInstance(error, DatabaseError)
        self.assertIsInstance(error, Exception)


class TestServiceError(unittest.TestCase):
    """Pruebas para ServiceError"""
    
    def test_service_error_is_exception(self):
        """Prueba que ServiceError hereda de Exception"""
        self.assertTrue(issubclass(ServiceError, Exception))
    
    def test_service_error_can_be_raised(self):
        """Prueba que ServiceError puede ser lanzada"""
        with self.assertRaises(ServiceError):
            raise ServiceError("Error de servicio")
    
    def test_service_error_with_message(self):
        """Prueba que ServiceError puede llevar un mensaje"""
        message = "Servicio no disponible"
        try:
            raise ServiceError(message)
        except ServiceError as e:
            self.assertEqual(str(e), message)
    
    def test_service_error_without_message(self):
        """Prueba que ServiceError puede ser lanzada sin mensaje"""
        try:
            raise ServiceError()
        except ServiceError as e:
            self.assertEqual(str(e), "")
    
    def test_service_error_can_be_caught_as_exception(self):
        """Prueba que ServiceError puede ser capturada como Exception"""
        with self.assertRaises(Exception):
            raise ServiceError("Error")
    
    def test_service_error_instance(self):
        """Prueba que se puede crear una instancia de ServiceError"""
        error = ServiceError("Business logic error")
        self.assertIsInstance(error, ServiceError)
        self.assertIsInstance(error, Exception)


class TestExceptionsInteraction(unittest.TestCase):
    """Pruebas de interacción entre excepciones"""
    
    def test_different_exceptions_are_distinct(self):
        """Prueba que las excepciones son tipos distintos"""
        validation_error = ValidationError("Validation")
        database_error = DatabaseError("Database")
        service_error = ServiceError("Service")
        
        self.assertNotIsInstance(validation_error, DatabaseError)
        self.assertNotIsInstance(validation_error, ServiceError)
        self.assertNotIsInstance(database_error, ValidationError)
        self.assertNotIsInstance(database_error, ServiceError)
        self.assertNotIsInstance(service_error, ValidationError)
        self.assertNotIsInstance(service_error, DatabaseError)
    
    def test_catch_specific_exception(self):
        """Prueba que se puede capturar una excepción específica"""
        def raise_validation_error():
            raise ValidationError("Validation failed")
        
        with self.assertRaises(ValidationError):
            raise_validation_error()
        
        # No debe capturar otros tipos de excepciones
        def raise_database_error():
            raise DatabaseError("DB failed")
        
        with self.assertRaises(DatabaseError):
            raise_database_error()
    
    def test_all_exceptions_can_be_caught_as_exception(self):
        """Prueba que todas las excepciones pueden ser capturadas como Exception base"""
        exceptions = [
            ValidationError("Validation"),
            DatabaseError("Database"),
            ServiceError("Service")
        ]
        
        for exc in exceptions:
            with self.assertRaises(Exception):
                raise exc
    
    def test_exception_with_multiple_args(self):
        """Prueba que las excepciones pueden recibir múltiples argumentos"""
        error = ValidationError("Error", "Additional info", 400)
        self.assertEqual(error.args, ("Error", "Additional info", 400))


if __name__ == '__main__':
    unittest.main()

