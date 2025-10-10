import os

class Config:

    SECRET_KEY = 'mi-clave-secreta-para-desarrollo' 
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://admin:123456@localhost:5432/software' 
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
