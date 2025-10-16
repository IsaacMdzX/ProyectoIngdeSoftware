import os

class Config:

    SECRET_KEY = 'mi-clave-secreta-para-desarrollo' 
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://admin:12345@localhost:5432/tienda_sneakers' 
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False