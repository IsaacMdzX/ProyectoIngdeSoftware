from flask import Flask
from config.config import Config
from .extensions import db, bcrypt

def create_app(config_class=Config):
    app = Flask(__name__)
    
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)

    from .auth.routes import auth_bp
    app.register_blueprint(auth_bp)

    from .admin.routes import admin_bp
    app.register_blueprint(admin_bp)

    from .public.routes import public_bp
    app.register_blueprint(public_bp)
    
    return app