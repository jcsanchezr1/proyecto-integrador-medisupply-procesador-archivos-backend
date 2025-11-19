"""
Servicio base - Estructura base para servicios con lógica de negocio
"""
from typing import Any, List, Optional


class BaseService:
    """Servicio base con operaciones comunes"""
    
    def validate_business_rules(self, **kwargs) -> None:
        """Valida las reglas de negocio"""
        # Implementar validaciones específicas en subclases
        pass
    
    def create(self, **kwargs) -> Any:
        """Crea una nueva entidad"""
        raise NotImplementedError("Método create debe ser implementado en subclases")
    
    def get_by_id(self, entity_id: str) -> Optional[Any]:
        """Obtiene una entidad por ID"""
        raise NotImplementedError("Método get_by_id debe ser implementado en subclases")
    
    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[Any]:
        """Obtiene todas las entidades"""
        raise NotImplementedError("Método get_all debe ser implementado en subclases")
    
    def update(self, entity_id: str, **kwargs) -> Any:
        """Actualiza una entidad"""
        raise NotImplementedError("Método update debe ser implementado en subclases")
    
    def delete(self, entity_id: str) -> bool:
        """Elimina una entidad"""
        raise NotImplementedError("Método delete debe ser implementado en subclases")

