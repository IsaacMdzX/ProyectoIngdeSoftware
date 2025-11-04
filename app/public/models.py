from ..extensions import db

class Marca(db.Model):
    __tablename__ = 'marcas'
    __table_args__ = {'schema': 'productos'}
    
    id_marca = db.Column(db.Integer, primary_key=True)
    nombre_marca = db.Column(db.String(100), unique=True, nullable=False)
    
    tenis = db.relationship('Tenis', backref='marca_info', lazy=True)
    playeras = db.relationship('Playera', backref='marca_info', lazy=True)

class Color(db.Model):
    __tablename__ = 'colores'
    __table_args__ = {'schema': 'productos'}
    id_color = db.Column(db.Integer, primary_key=True)
    nombre_color = db.Column(db.String(50), unique=True, nullable=False)

class Genero(db.Model):
    __tablename__ = 'generos'
    __table_args__ = {'schema': 'productos'}
    id_genero = db.Column(db.Integer, primary_key=True)
    nombre_genero = db.Column(db.String(20), unique=True, nullable=False)

class TallaCalzado(db.Model):
    __tablename__ = 'tallas_calzado'
    __table_args__ = {'schema': 'productos'}
    id_talla_calzado = db.Column(db.Integer, primary_key=True)
    numero_talla = db.Column(db.Numeric(4, 1), unique=True, nullable=False)

class TallaRopa(db.Model):
    __tablename__ = 'tallas_ropa'
    __table_args__ = {'schema': 'productos'}
    id_talla_ropa = db.Column(db.Integer, primary_key=True)
    nombre_talla = db.Column(db.String(10), unique=True, nullable=False)

class TipoProducto(db.Model):
    __tablename__ = 'tipos_producto'
    __table_args__ = {'schema': 'productos'}
    id_tipo_producto = db.Column(db.Integer, primary_key=True)
    nombre_tipo = db.Column(db.String(50), unique=True, nullable=False)

class Tenis(db.Model):
    __tablename__ = 'tenis'
    __table_args__ = {'schema': 'productos'}
    
    id_teni = db.Column(db.Integer, primary_key=True)
    nombre_tenis = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.Integer, db.ForeignKey('productos.marcas.id_marca'), nullable=False)
    tipo = db.Column(db.Integer, db.ForeignKey('productos.tipos_producto.id_tipo_producto'), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    talla_calzado = db.Column(db.Integer, db.ForeignKey('productos.tallas_calzado.id_talla_calzado'))
    
class Playera(db.Model):
    __tablename__ = 'playeras'
    __table_args__ = {'schema': 'productos'}
    
    id_playera = db.Column(db.Integer, primary_key=True)
    nombre_playera = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.Integer, db.ForeignKey('productos.marcas.id_marca'), nullable=False)
    material = db.Column(db.String(50))
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    tipo = db.Column(db.Integer, db.ForeignKey('productos.tipos_producto.id_tipo_producto'))
    talla_ropa = db.Column(db.Integer, db.ForeignKey('productos.tallas_ropa.id_talla_ropa'))
    genero = db.Column(db.Integer, db.ForeignKey('productos.generos.id_genero'))

class Gorra(db.Model):
    __tablename__ = 'gorras'
    __table_args__ = {'schema': 'productos'}
    
    id_gorra = db.Column(db.Integer, primary_key=True)
    nombre_gorra = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    talla_ropa = db.Column(db.Integer, db.ForeignKey('productos.tallas_ropa.id_talla_ropa'))