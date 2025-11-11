import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'tu-clave-secreta-debe-ser-muy-dificil'
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://admin:123456@localhost:5432/sneakers_store'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False