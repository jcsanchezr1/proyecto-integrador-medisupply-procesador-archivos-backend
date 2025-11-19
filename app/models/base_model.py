"""
Modelo base - Estructura base para todos los modelos
"""
from typing import Dict, Any


class BaseModel:
    """Modelo base con operaciones comunes"""
    
    def __init__(self, **kwargs):
        """Inicializa el modelo con los datos proporcionados"""
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario"""
        return {
            key: value for key, value in self.__dict__.items()
            if not key.startswith('_')
        }
    
    def validate(self) -> bool:
        """Valida los datos del modelo"""
        # Implementar validaciones específicas en subclases
        return True
    
    def __repr__(self) -> str:
        """Representación en string del modelo"""
        return f"{self.__class__.__name__}({self.to_dict()})"

