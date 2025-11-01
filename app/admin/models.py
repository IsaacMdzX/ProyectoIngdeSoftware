from ..extensions import db

class Inventario(db.Model):
    __tablename__ = 'inventario'
    __table_args__ = {'schema': 'stock'}
    
    id_inventario = db.Column(db.Integer, primary_key=True)
    tipo_producto = db.Column(db.String(20), nullable=False)
    id_producto = db.Column(db.Integer, nullable=False)
    cantidad = db.Column(db.Integer, default=0, nullable=False)
    fecha_registro = db.Column(db.DateTime, default=db.func.now())
    ultima_actualizacion = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())