from flask import Flask
from dotenv import load_dotenv
import os
from config.config import Config
from .extensions import db, bcrypt

def create_app(config_class=Config):
    # Cargar variables del archivo .env si existe (MP_ACCESS_TOKEN, SECRET_KEY, etc.)
    # Forzar ruta absoluta al archivo .env ubicado en la raíz del proyecto
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    env_path = os.path.join(base_dir, '.env')
    load_dotenv(env_path)
    app = Flask(__name__)
    
    app.config.from_object(config_class)
    # Exponer el token también en la configuración de Flask por si os.environ falla en tiempo de
    # ejecución de algún proceso o shell diferente
    app.config['MP_ACCESS_TOKEN'] = os.environ.get('MP_ACCESS_TOKEN')
    # Base pública opcional (https) para construir back_urls de Mercado Pago en vez de localhost
    # Ejemplo: https://<tu-dominio-o-tunnel>
    app.config['EXTERNAL_BASE_URL'] = os.environ.get('EXTERNAL_BASE_URL')
    # Teléfono de WhatsApp para recibir comprobantes (formato internacional sin '+', ej. 5215512345678)
    app.config['WHATSAPP_PHONE'] = os.environ.get('WHATSAPP_PHONE', '5215512345678')

    # PayPal removido del flujo actual; si se requiere en el futuro, reactivar aquí.

    db.init_app(app)
    bcrypt.init_app(app)

    from .auth.routes import auth_bp
    app.register_blueprint(auth_bp)

    from .admin.routes import admin_bp
    app.register_blueprint(admin_bp)

    from .public.routes import public_bp
    app.register_blueprint(public_bp)
    
    return app