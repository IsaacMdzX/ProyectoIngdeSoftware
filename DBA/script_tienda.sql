create schema stock;
create schema productos;
create schema usuarios;
create schema ventas;

CREATE TABLE productos.marcas (id_marca SERIAL PRIMARY KEY, nombre_marca VARCHAR(100) UNIQUE NOT NULL);

create table productos.tenis (Id_teni serial primary key, Nombre_tenis varchar(100) not null, Marca int not null,Tipo int not null, Talla numeric(4,1) not null,Color varchar(50),Descripcion text,Precio decimal(10,2) not null,CONSTRAINT fk_marca_tenis FOREIGN KEY (Marca) REFERENCES productos.marcas(id_marca));  

create table productos.Gorras (Id_gorra serial primary key, Nombre_gorra varchar(100) unique not null, Talla varchar (10) not null, Color varchar (50) not null,Descripcion text, Precio decimal(10,2) not null);

create table productos.playeras (Id_playera serial primary key, Nombre_playera varchar(100) not null,Marca int not null, Talla varchar(10) not null, Color varchar(50) not null, Material varchar (50), Genero VARCHAR(20) CHECK (genero IN ('Hombre','Mujer','Unisex')), Descripcion text, Precio decimal (10,2) not null, CONSTRAINT fk_marca_tenis FOREIGN KEY (Marca) REFERENCES productos.marcas(id_marca));

Create table stock.inventario (Id_inventario serial Primary key, Tipo_producto varchar(20) not null check(tipo_producto in ('Playera','Tenis','Gorra')),id_producto int not null, Cantidad int not null default 0, Fecha_registro timestamp default now(), Ultima_actualizacion timestamp default now(), CONSTRAINT fk_playera FOREIGN KEY (id_producto) REFERENCES productos.playeras(id_playera) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_tenis FOREIGN KEY (id_producto) REFERENCES productos.tenis(id_teni) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_gorra FOREIGN KEY (id_producto) REFERENCES productos.gorras(id_gorra) DEFERRABLE INITIALLY DEFERRED);

create table ventas.usuarios(Id_usua serial primary key, Nombre_usua varchar(100) not null, Email varchar(150) unique not null, telefono varchar (20), Direccion text,  Fecha_registro timestamp default now(), Constraint chk_email_valido check(email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'));

CREATE TABLE ventas.transferencias (
  Id_transf SERIAL PRIMARY KEY,
  Id_cliente INT NOT NULL,
  Origen VARCHAR(100) NOT NULL,
  Destino VARCHAR(100) NOT NULL,
  Comision DECIMAL(10,2) DEFAULT 0 CHECK(Comision >= 0),
  Concepto VARCHAR(200),
  Tipo_operacion VARCHAR(50) NOT NULL,
  Folio VARCHAR(50) UNIQUE NOT NULL,
  Fecha DATE DEFAULT CURRENT_DATE,
  Monto DECIMAL(10,2) NOT NULL CHECK (Monto >= 0),
  CONSTRAINT FK_cliente_transferencia FOREIGN KEY (Id_cliente)
      REFERENCES usuarios.cliente(Id_cliente)
);


CREATE TABLE ventas.pedidos (
  Id_pedidos SERIAL PRIMARY KEY,
  Id_cliente INT NOT NULL,
  Fecha_pedido TIMESTAMP DEFAULT NOW(),
  Estado VARCHAR(20) NOT NULL CHECK (Estado IN ('Pendiente','Pagado','Enviado','Entregado','Cancelado')),
  Total DECIMAL (10,2) NOT NULL DEFAULT 0,
  CONSTRAINT fk_pedido_cliente FOREIGN KEY (Id_cliente)
      REFERENCES usuarios.cliente(Id_cliente)
);

CREATE TABLE ventas.detalle_pedido (
    Id_dep SERIAL PRIMARY KEY,
    Id_pedido INT NOT NULL,
    Tipo_producto VARCHAR(20) NOT NULL CHECK (Tipo_producto IN ('Playera', 'Tenis', 'Gorra')),
    Id_producto INT NOT NULL,
    Cantidad INT NOT NULL CHECK (Cantidad > 0),
    Precio_unitario DECIMAL(10,2) NOT NULL CHECK (Precio_unitario >= 0),
    Subtotal DECIMAL(10,2) GENERATED ALWAYS AS (Cantidad * Precio_unitario) STORED,
    CONSTRAINT fk_detalle_pedido FOREIGN KEY (Id_pedido)REFERENCES ventas.pedidos(Id_pedidos)ON DELETE CASCADE,CONSTRAINT fk_detalle_playera FOREIGN KEY (Id_producto)
        REFERENCES productos.playeras(Id_playera)
        DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_detalle_tenis FOREIGN KEY (Id_producto)
        REFERENCES productos.tenis(Id_teni)
        DEFERRABLE INITIALLY DEFERRED,

    CONSTRAINT fk_detalle_gorra FOREIGN KEY (Id_producto)
        REFERENCES productos.gorras(Id_gorra)
        DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE ventas.entregas (
    id_entrega SERIAL PRIMARY KEY,
    id_pedido INT NOT NULL,
    direccion_entrega TEXT NOT NULL,
    fecha_entrega TIMESTAMP,
    estado VARCHAR(20) NOT NULL CHECK (estado IN ('Pendiente','En camino','Entregado')),
    CONSTRAINT fk_entrega_pedido FOREIGN KEY (id_pedido) REFERENCES ventas.pedidos(id_pedidos) ON DELETE CASCADE
);
