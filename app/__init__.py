from flask import Flask
from config import Config                 
from database import setup_database 
from .auth import auth_bp
from .main import main_bp
from flask import Flask, redirect, url_for
import os

def create_app(config_class=Config):

    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    
    app.config.from_object(config_class)

    
    setup_database(app) 
    
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp) 
    
    @app.route('/')
    def index():
        return redirect('/auth/login')

    return app 



    
   