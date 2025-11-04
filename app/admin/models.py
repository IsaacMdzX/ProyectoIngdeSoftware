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

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    __table_args__ = {'schema': 'ventas'}
    
    id_pedidos = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('usuarios.cliente.id_cliente'), nullable=False)
    fecha_pedido = db.Column(db.DateTime, default=db.func.now())
    estado = db.Column(db.String(20), nullable=False)
    total = db.Column(db.Numeric(10, 2), default=0, nullable=False)

class DetallePedido(db.Model):
    __tablename__ = 'detalle_pedido'
    __table_args__ = {'schema': 'ventas'}
    
    id_dep = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey('ventas.pedidos.id_pedidos', ondelete='CASCADE'), nullable=False)
    tipo_producto = db.Column(db.String(20), nullable=False)
    id_producto = db.Column(db.Integer, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), db.Computed('cantidad * precio_unitario', persisted=True))

class Entrega(db.Model):
    __tablename__ = 'entregas'
    __table_args__ = {'schema': 'ventas'}
    
    id_entrega = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey('ventas.pedidos.id_pedidos', ondelete='CASCADE'), nullable=False)
    direccion_entrega = db.Column(db.Text, nullable=False)
    fecha_entrega = db.Column(db.DateTime)
    estado = db.Column(db.String(20), nullable=False)

class Transferencia(db.Model):
    __tablename__ = 'transferencias'
    __table_args__ = {'schema': 'ventas'}
    
    id_transf = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('usuarios.cliente.id_cliente'), nullable=False)
    origen = db.Column(db.String(100), nullable=False)
    destino = db.Column(db.String(100), nullable=False)
    comision = db.Column(db.Numeric(10, 2), default=0)
    concepto = db.Column(db.String(200))
    tipo_operacion = db.Column(db.String(50), nullable=False)
    folio = db.Column(db.String(50), unique=True, nullable=False)
    fecha = db.Column(db.Date, default=db.func.current_date())
    monto = db.Column(db.Numeric(10, 2), nullable=False)