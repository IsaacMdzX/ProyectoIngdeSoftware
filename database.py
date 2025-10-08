from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def setup_database(app):
    """Inicializa el objeto db con la aplicación Flask."""
    db.init_app(app)


class Marca(db.Model):
    __tablename__ = 'marcas'
    __table_args__ = {'schema': 'productos'}
    
    id_marca = db.Column(db.Integer, primary_key=True)
    nombre_marca = db.Column(db.String(100), unique=True, nullable=False)
    
    # Relationships
    tenis = db.relationship('Tenis', backref='marca_info', lazy=True)
    playeras = db.relationship('Playera', backref='marca_info', lazy=True)
    
    def __repr__(self):
        return f'<Marca {self.nombre_marca}>'


class Tenis(db.Model):
    __tablename__ = 'tenis'
    __table_args__ = {'schema': 'productos'}
    
    id_tenis = db.Column(db.Integer, primary_key=True)
    nombre_tenis = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.Integer, db.ForeignKey('productos.marcas.id_marca'), nullable=False)
    tipo = db.Column(db.Integer, nullable=False)
    talla = db.Column(db.Numeric(4, 1), nullable=False)
    color = db.Column(db.String(50))
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    
    def __repr__(self):
        return f'<Tenis {self.nombre_tenis}>'


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
    
    def __repr__(self):
        return f'<Playera {self.nombre_playera}>'


class Gorra(db.Model):
    __tablename__ = 'gorras'
    __table_args__ = {'schema': 'productos'}
    
    id_gorra = db.Column(db.Integer, primary_key=True)
    nombre_gorra = db.Column(db.String(100), unique=True, nullable=False)
    talla = db.Column(db.String(10), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    
    def __repr__(self):
        return f'<Gorra {self.nombre_gorra}>'


class Inventario(db.Model):
    __tablename__ = 'inventario'
    __table_args__ = {'schema': 'stock'}
    
    id_inventario = db.Column(db.Integer, primary_key=True)
    tipo_producto = db.Column(db.String(20), nullable=False)
    id_producto = db.Column(db.Integer, nullable=False)
    cantidad = db.Column(db.Integer, default=0, nullable=False)
    fecha_registro = db.Column(db.DateTime, default=db.func.now())
    ultima_actualizacion = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    def __repr__(self):
        return f'<Inventario {self.tipo_producto}-{self.id_producto}: {self.cantidad}>'


class Cliente(db.Model):
    __tablename__ = 'cliente'
    __table_args__ = {'schema': 'usuarios'}
    
    id_cliente = db.Column(db.Integer, primary_key=True)
    nombre_cliente = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.Text)
    fecha_registro = db.Column(db.DateTime, default=db.func.now())
    
    # Relationships
    pedidos = db.relationship('Pedido', backref='cliente_info', lazy=True)
    transferencias = db.relationship('Transferencia', backref='cliente_info', lazy=True)
    
    def __repr__(self):
        return f'<Cliente {self.nombre_cliente} - {self.email}>'


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
    
    def __repr__(self):
        return f'<Transferencia {self.folio} - ${self.monto}>'


class Pedido(db.Model):
    __tablename__ = 'pedidos'
    __table_args__ = {'schema': 'ventas'}
    
    id_pedidos = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('usuarios.cliente.id_cliente'), nullable=False)
    fecha_pedido = db.Column(db.DateTime, default=db.func.now())
    estado = db.Column(db.String(20), nullable=False)
    total = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    
    # Relationships
    detalles = db.relationship('DetallePedido', backref='pedido', lazy=True, cascade='all, delete-orphan')
    entregas = db.relationship('Entrega', backref='pedido', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Pedido #{self.id_pedidos} - {self.estado}>'


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
    
    def __repr__(self):
        return f'<DetallePedido {self.tipo_producto}-{self.id_producto} x{self.cantidad}>'


class Entrega(db.Model):
    __tablename__ = 'entregas'
    __table_args__ = {'schema': 'ventas'}
    
    id_entrega = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey('ventas.pedidos.id_pedidos', ondelete='CASCADE'), nullable=False)
    direccion_entrega = db.Column(db.Text, nullable=False)
    fecha_entrega = db.Column(db.DateTime)
    estado = db.Column(db.String(20), nullable=False)
    
    def __repr__(self):
        return f'<Entrega Pedido#{self.id_pedido} - {self.estado}>'