"""
Repositorio base - Estructura base para acceso a datos
"""
from typing import Any, List, Optional


class BaseRepository:
    """Repositorio base con operaciones CRUD comunes"""
    
    def __init__(self, session=None):
        """Inicializa el repositorio con una sesión de BD"""
        self.session = session
    
    def create(self, **kwargs) -> Any:
        """Crea un nuevo registro"""
        raise NotImplementedError("Método create debe ser implementado en subclases")
    
    def get_by_id(self, entity_id: str) -> Optional[Any]:
        """Obtiene un registro por ID"""
        raise NotImplementedError("Método get_by_id debe ser implementado en subclases")
    
    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[Any]:
        """Obtiene todos los registros"""
        raise NotImplementedError("Método get_all debe ser implementado en subclases")
    
    def update(self, entity_id: str, **kwargs) -> Any:
        """Actualiza un registro"""
        raise NotImplementedError("Método update debe ser implementado en subclases")
    
    def delete(self, entity_id: str) -> bool:
        """Elimina un registro"""
        raise NotImplementedError("Método delete debe ser implementado en subclases")
    
    def exists(self, entity_id: str) -> bool:
        """Verifica si un registro existe"""
        raise NotImplementedError("Método exists debe ser implementado en subclases")

