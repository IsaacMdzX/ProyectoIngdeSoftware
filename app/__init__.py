from flask import Flask
from config import Config                 
from database import setup_database 
from .auth import auth_bp
from flask import Flask, redirect, url_for
import os

def create_app(config_class=Config):
    """
    Función de fábrica para crear la instancia de la aplicación Flask.
    """
    
    
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'),
                static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'))
    
    
    app.config.from_object(config_class)

    
    setup_database(app) 
    
    
    app.register_blueprint(auth_bp) 
    
    @app.route('/')
    def index():
        return redirect('/auth/login')

    return app 



    
   