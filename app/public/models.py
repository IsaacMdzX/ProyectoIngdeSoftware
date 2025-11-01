from ..extensions import db

class Marca(db.Model):
    __tablename__ = 'marcas'
    __table_args__ = {'schema': 'productos'}
    
    id_marca = db.Column(db.Integer, primary_key=True)
    nombre_marca = db.Column(db.String(100), unique=True, nullable=False)
    
    tenis = db.relationship('Tenis', backref='marca_info', lazy=True)
    playeras = db.relationship('Playera', backref='marca_info', lazy=True)

class Tenis(db.Model):
    __tablename__ = 'tenis'
    __table_args__ = {'schema': 'productos'}
    
    id_teni = db.Column(db.Integer, primary_key=True)
    nombre_tenis = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.Integer, db.ForeignKey('productos.marcas.id_marca'), nullable=False)
    tipo = db.Column(db.Integer, nullable=False)
    talla = db.Column(db.Numeric(4, 1), nullable=False)
    color = db.Column(db.String(50))
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric(10, 2), nullable=False)

class Playera(db.Model):
    __tablename__ = 'playeras'
    __table_args__ = {'schema': 'productos'}
    
    id_playera = db.Column(db.Integer, primary_key=True)
    nombre_playera = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.Integer, db.ForeignKey('productos.marcas.id_marca'), nullable=False)
    talla = db.Column(db.String(10), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    material = db.Column(db.String(50))
    genero = db.Column(db.String(20)) 
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric(10, 2), nullable=False)

class Gorra(db.Model):
    __tablename__ = 'gorras'
    __table_args__ = {'schema': 'productos'}
    
    id_gorra = db.Column(db.Integer, primary_key=True)
    nombre_gorra = db.Column(db.String(100), unique=True, nullable=False)
    talla = db.Column(db.String(10), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric(10, 2), nullable=False)