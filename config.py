import os

class Config:
    """Configuración de la aplicación Flask."""
    
    # Base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://admin:123456@localhost:5432/software'
    
    # Desactivar señales de modificación (mejora performance)
    SQLALCHEMY_TRACK_MODIFICATIONS = False