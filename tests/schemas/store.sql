CREATE DATABASE IF NOT EXISTS prueba_fn CHARACTER
SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE prueba_fn;

-- Tabla 1: diseño correcto (esperado: Verde hasta BCNF)
CREATE TABLE cliente (
    cliente_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    rfc VARCHAR(13) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(120) NOT NULL,
    PRIMARY KEY (cliente_id),
    UNIQUE KEY uq_cliente_rfc (rfc)
    -- FD: (cliente_id) -> (rfc, nombre, correo)
    -- FD: (rfc) -> (cliente_id, nombre, correo)
) ENGINE = InnoDB;

-- Tabla 2: llave compuesta con dependencias parciales y transitivas
-- (esperado: 2FN Rojo por producto_id -> nombre_producto, precio_unitario;
    --            3FN Rojo por categoria_id -> nombre_categoria)
CREATE TABLE pedido_detalle (
    pedido_id INT UNSIGNED NOT NULL,
    producto_id INT UNSIGNED NOT NULL,
    cliente_id INT UNSIGNED NOT NULL,
    nombre_producto VARCHAR(100) NOT NULL,
    precio_unitario DECIMAL(10, 2) NOT NULL,
    categoria_id INT UNSIGNED NOT NULL,
    nombre_categoria VARCHAR(60) NOT NULL,
    cantidad INT UNSIGNED NOT NULL DEFAULT 1,
    PRIMARY KEY (pedido_id, producto_id),
    CONSTRAINT fk_detalle_cliente FOREIGN KEY (cliente_id) REFERENCES cliente (cliente_id)
    -- FD: (pedido_id, producto_id) -> (cantidad)
    -- FD: (pedido_id) -> (cliente_id)
    -- FD: (producto_id) -> (nombre_producto, precio_unitario, categoria_id)
    -- FD: (categoria_id) -> (nombre_categoria)
) ENGINE = InnoDB;
