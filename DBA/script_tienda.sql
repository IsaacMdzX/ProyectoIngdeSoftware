create schema productos;
create schema stock;
create schema usuarios;
create schema ventas;

CREATE TABLE productos.marcas (
    id_marca SERIAL PRIMARY KEY,
    nombre_marca VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE productos.tipos_producto (
    id_tipo_producto SERIAL PRIMARY KEY,
    nombre_tipo VARCHAR(50) UNIQUE NOT NULL CHECK (nombre_tipo IN ('Playera','Tenis','Gorra'))
);

CREATE TABLE productos.generos (
    id_genero SERIAL PRIMARY KEY,
    nombre_genero VARCHAR(20) UNIQUE NOT NULL CHECK (nombre_genero IN ('Hombre','Mujer','Unisex'))
);

CREATE TABLE productos.tallas_ropa (
    id_talla_ropa SERIAL PRIMARY KEY,
    nombre_talla VARCHAR(10) UNIQUE NOT NULL CHECK (nombre_talla IN ('XS','S','M','L','XL','XXL','Única'))
);

CREATE TABLE productos.tallas_calzado (
    id_talla_calzado SERIAL PRIMARY KEY,
    numero_talla NUMERIC(4,1) UNIQUE NOT NULL CHECK (numero_talla > 0)
);

CREATE TABLE productos.colores (
    id_color SERIAL PRIMARY KEY,
    nombre_color VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE productos.playeras (
    Id_playera SERIAL PRIMARY KEY, 
    Nombre_playera VARCHAR(100) NOT NULL,
    Marca INT NOT NULL, 
    Tipo INT NOT NULL, 
    Talla_ropa INT NOT NULL, 
    Material VARCHAR (50), 
    Genero INT, 
    Descripcion TEXT, 
    Precio DECIMAL (10,2) NOT NULL, 
    CONSTRAINT fk_marca_playera FOREIGN KEY (Marca) REFERENCES productos.marcas(id_marca),
    CONSTRAINT fk_tipo_playera FOREIGN KEY (Tipo) REFERENCES productos.tipos_producto(id_tipo_producto),
    CONSTRAINT fk_talla_playera FOREIGN KEY (Talla_ropa) REFERENCES productos.tallas_ropa(id_talla_ropa),
    CONSTRAINT fk_genero_playera FOREIGN KEY (Genero) REFERENCES productos.generos(id_genero)
);

CREATE TABLE productos.playeras_colores (
    id_pc SERIAL PRIMARY KEY,
    id_playera INT NOT NULL,
    id_color INT NOT NULL,
    UNIQUE (id_playera, id_color), 
    CONSTRAINT fk_pc_playera FOREIGN KEY (id_playera) 
        REFERENCES productos.playeras(id_playera) ON DELETE CASCADE,
    CONSTRAINT fk_pc_color FOREIGN KEY (id_color) 
        REFERENCES productos.colores(id_color) ON DELETE RESTRICT
);

CREATE TABLE productos.tenis (
    Id_teni SERIAL PRIMARY KEY, 
    Nombre_tenis VARCHAR(100) NOT NULL, 
    Marca INT NOT NULL,
    Tipo INT NOT NULL, 
    Talla_calzado INT NOT NULL, 
    Descripcion TEXT,
    Precio DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_marca_tenis FOREIGN KEY (Marca) REFERENCES productos.marcas(id_marca),
    CONSTRAINT fk_tipo_tenis FOREIGN KEY (Tipo) REFERENCES productos.tipos_producto(id_tipo_producto),
    CONSTRAINT fk_talla_tenis FOREIGN KEY (Talla_calzado) REFERENCES productos.tallas_calzado(id_talla_calzado)
);  

CREATE TABLE productos.tenis_colores (
    id_tc SERIAL PRIMARY KEY,
    id_teni INT NOT NULL,
    id_color INT NOT NULL,
    UNIQUE (id_teni, id_color), 
    CONSTRAINT fk_tc_teni FOREIGN KEY (id_teni) 
        REFERENCES productos.tenis(id_teni) ON DELETE CASCADE,
    CONSTRAINT fk_tc_color FOREIGN KEY (id_color) 
        REFERENCES productos.colores(id_color) ON DELETE RESTRICT
);

CREATE TABLE productos.gorras (
    Id_gorra SERIAL PRIMARY KEY, 
    Nombre_gorra VARCHAR(100) UNIQUE NOT NULL, 
    Talla_ropa INT NOT NULL, 
    Descripcion TEXT, 
    Precio DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_talla_gorra FOREIGN KEY (Talla_ropa) REFERENCES productos.tallas_ropa(id_talla_ropa)
);

CREATE TABLE productos.gorras_colores (
    id_gc SERIAL PRIMARY KEY,
    id_gorra INT NOT NULL,
    id_color INT NOT NULL,
    UNIQUE (id_gorra, id_color), 
    CONSTRAINT fk_gc_gorra FOREIGN KEY (id_gorra) 
        REFERENCES productos.gorras(id_gorra) ON DELETE CASCADE,
    CONSTRAINT fk_gc_color FOREIGN KEY (id_color) 
        REFERENCES productos.colores(id_color) ON DELETE RESTRICT
);

CREATE TABLE stock.inventario (
    Id_inventario SERIAL PRIMARY KEY, 
    Tipo_producto VARCHAR(20) NOT NULL CHECK(tipo_producto IN ('Playera','Tenis','Gorra')),
    id_producto INT NOT NULL, 
    Cantidad INT NOT NULL DEFAULT 0, 
    Fecha_registro TIMESTAMP DEFAULT NOW(), 
    Ultima_actualizacion TIMESTAMP DEFAULT NOW(), 
    CONSTRAINT fk_inventario_playera FOREIGN KEY (id_producto) 
        REFERENCES productos.playeras(id_playera) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_inventario_tenis FOREIGN KEY (id_producto) 
        REFERENCES productos.tenis(id_teni) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_inventario_gorra FOREIGN KEY (id_producto) 
        REFERENCES productos.gorras(id_gorra) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE usuarios.cliente(
    Id_cliente SERIAL PRIMARY KEY, 
    Nombre_cliente VARCHAR(100) NOT NULL, 
    Email VARCHAR(150) UNIQUE NOT NULL, 
    telefono VARCHAR (20), 
    Fecha_registro TIMESTAMP DEFAULT NOW(), 
    Contrasena VARCHAR(255) NOT NULL, 
    CONSTRAINT chk_email_valido_cliente 
        CHECK(Email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT chk_contrasena_compleja_cliente
        CHECK (Contrasena ~ '^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).{8,}$')
);

CREATE TABLE usuarios.admin (
    Id_admin SERIAL PRIMARY KEY,
    Nombre_admin VARCHAR(100) NOT NULL,
    Correo VARCHAR(150) UNIQUE NOT NULL,
    Telefono VARCHAR (20) NOT NULL,
    Contrasena VARCHAR(255) NOT NULL,
    CONSTRAINT chk_email_valido_admin 
        CHECK(Correo ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT chk_contrasena_compleja_admin
        CHECK (Contrasena ~ '^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).{8,}$')
);

CREATE TABLE ventas.pedidos (
    Id_pedidos SERIAL PRIMARY KEY,
    Id_cliente INT NOT NULL,
    Fecha_pedido TIMESTAMP DEFAULT NOW(),
    Estado VARCHAR(20) NOT NULL CHECK (Estado IN ('Pendiente','Pagado','Enviado','Entregado','Cancelado')),
    Total DECIMAL (10,2) NOT NULL DEFAULT 0, 
    CONSTRAINT fk_pedido_cliente FOREIGN KEY (Id_cliente) REFERENCES usuarios.cliente(Id_cliente)
);

CREATE TABLE ventas.detalle_pedido (
    Id_dep SERIAL PRIMARY KEY,
    Id_pedido INT NOT NULL,
    Tipo_producto VARCHAR(20) NOT NULL CHECK (Tipo_producto IN ('Playera', 'Tenis', 'Gorra')),
    Id_producto INT NOT NULL,
    Cantidad INT NOT NULL CHECK (Cantidad > 0),
    Precio_unitario DECIMAL(10,2) NOT NULL CHECK (Precio_unitario >= 0),
    Subtotal DECIMAL(10,2) GENERATED ALWAYS AS (Cantidad * Precio_unitario) STORED,
    CONSTRAINT fk_detalle_pedido FOREIGN KEY (Id_pedido) REFERENCES ventas.pedidos(Id_pedidos) ON DELETE CASCADE,
    CONSTRAINT fk_detalle_playera FOREIGN KEY (Id_producto)
        REFERENCES productos.playeras(Id_playera) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_detalle_tenis FOREIGN KEY (Id_producto)
        REFERENCES productos.tenis(Id_teni) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_detalle_gorra FOREIGN KEY (Id_producto)
        REFERENCES productos.gorras(Id_gorra) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE ventas.entregas (
    id_entrega SERIAL PRIMARY KEY,
    id_pedido INT NOT NULL,
    direccion_entrega TEXT NOT NULL,
    fecha_entrega TIMESTAMP,
    estado VARCHAR(20) NOT NULL CHECK (estado IN ('Pendiente','En camino','Entregado')),
    CONSTRAINT fk_entrega_pedido FOREIGN KEY (id_pedido) REFERENCES ventas.pedidos(id_pedidos) ON DELETE CASCADE
);

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
-- 1️ Ingreso de Tipos de Producto
INSERT INTO productos.tipos_producto (nombre_tipo) VALUES
('Playera'),
('Tenis'),
('Gorra');

--  Ingreso de Géneros
INSERT INTO productos.generos (nombre_genero) VALUES
('Hombre'),
('Mujer'),
('Unisex');

-- Ingreso de Tallas de Ropa
INSERT INTO productos.tallas_ropa (nombre_talla) VALUES
('XS'), ('S'), ('M'), ('L'), ('XL'), ('XXL'), ('Única');

--Ingreso de Tallas de Calzado
INSERT INTO productos.tallas_calzado (numero_talla) VALUES
(5.0), (6.0), (7.0), (7.5), (8.0), (8.5), (9.0), (9.5), (10.0), (10.5), (11.0);

-- Ingreso de Marcas
INSERT INTO productos.marcas (nombre_marca) VALUES
('Nike'),
('Adidas'),
('Puma'),
('Reebok'),
('Under Armour');

--Ingreso de Colores
INSERT INTO productos.colores (nombre_color) VALUES
('Rojo'),
('Azul'),
('Verde'),
('Negro'),
('Blanco'),
('Amarillo'),
('Gris'),
('Naranja'),
('Morado'),
('Rosa');

--  Ingreso de Tenis
INSERT INTO productos.tenis (Nombre_tenis, Marca, Tipo, Talla_calzado, Descripcion, Precio) VALUES
(
    'Air Max 90',
    (SELECT id_marca FROM productos.marcas WHERE nombre_marca = 'Nike'),
    (SELECT id_tipo_producto FROM productos.tipos_producto WHERE nombre_tipo = 'Tenis'),
    (SELECT id_talla_calzado FROM productos.tallas_calzado WHERE numero_talla = 9.0),
    'Tenis casual Nike Air Max 90',
    119.99
),
(
    'Ultraboost',
    (SELECT id_marca FROM productos.marcas WHERE nombre_marca = 'Adidas'),
    (SELECT id_tipo_producto FROM productos.tipos_producto WHERE nombre_tipo = 'Tenis'),
    (SELECT id_talla_calzado FROM productos.tallas_calzado WHERE numero_talla = 9.5),
    'Tenis running Adidas Ultraboost',
    149.99
),
(
    'Suede Classic',
    (SELECT id_marca FROM productos.marcas WHERE nombre_marca = 'Puma'),
    (SELECT id_tipo_producto FROM productos.tipos_producto WHERE nombre_tipo = 'Tenis'),
    (SELECT id_talla_calzado FROM productos.tallas_calzado WHERE numero_talla = 9.0),
    'Tenis estilo urbano Puma Suede',
    79.50
);

--  Asociar colores a los tenis insertados
INSERT INTO productos.tenis_colores (id_teni, id_color)
SELECT t.Id_teni, c.id_color
FROM productos.tenis t
JOIN productos.colores c ON c.nombre_color IN ('Negro','Blanco','Azul')
WHERE t.Nombre_tenis = 'Air Max 90';

INSERT INTO productos.tenis_colores (id_teni, id_color)
SELECT t.Id_teni, c.id_color
FROM productos.tenis t
JOIN productos.colores c ON c.nombre_color IN ('Blanco','Negro')
WHERE t.Nombre_tenis = 'Ultraboost';

INSERT INTO productos.tenis_colores (id_teni, id_color)
SELECT t.Id_teni, c.id_color
FROM productos.tenis t
JOIN productos.colores c ON c.nombre_color IN ('Gris','Negro')
WHERE t.Nombre_tenis = 'Suede Classic';

---Consultas Ejecutarlas en psql no instalarlo 

SELECT
    t.id_teni,
    t.nombre_tenis AS nombre,
    m.nombre_marca AS marca,
    tp.nombre_tipo AS tipo,
    tc.numero_talla AS talla,
    t.precio,
    STRING_AGG(c.nombre_color, ', ') AS colores_disponibles
FROM productos.tenis t
JOIN productos.marcas m ON t.marca = m.id_marca
JOIN productos.tipos_producto tp ON t.tipo = tp.id_tipo_producto
JOIN productos.tallas_calzado tc ON t.talla_calzado = tc.id_talla_calzado
JOIN productos.tenis_colores tcl ON t.id_teni = tcl.id_teni
JOIN productos.colores c ON tcl.id_color = c.id_color
GROUP BY t.id_teni, t.nombre_tenis, m.nombre_marca, tp.nombre_tipo, tc.numero_talla, t.precio
ORDER BY t.id_teni;
