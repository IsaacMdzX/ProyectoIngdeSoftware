from ..extensions import db

class Cliente(db.Model):
    __tablename__ = 'cliente'
    __table_args__ = {'schema': 'usuarios'}
    
    id_cliente = db.Column(db.Integer, primary_key=True)
    nombre_cliente = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    fecha_registro = db.Column(db.DateTime, default=db.func.now())
    contrasena = db.Column(db.String(255), nullable=False)

class Admin(db.Model):
    __tablename__ = 'admin'
    __table_args__ = {'schema': 'usuarios'}
    
    id_admin = db.Column(db.Integer, primary_key=True)
    nombre_admin = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(150), unique=True, nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)