from flask import Flask, redirect, render_template, url_for
from config import Config
from database import setup_database
from .auth import auth_bp
from .main import main_bp
from routes.admin_routes import admin_bp
import os

def create_app(config_class=Config):
    app = Flask(__name__,
        template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
        static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    app.config.from_object(config_class)
    setup_database(app)
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    
    @app.route('/')
    def index():
        # 👇 CORREGIDO - usa el nombre correcto de la ruta
        return redirect(url_for('main.tenis'))  # O 'main.catalogo' según tus rutas
    
    return app


  #   return redirect(url_for('admin.admin_login'))