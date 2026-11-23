USE WankaAgroDB;
GO

-- 1. Distritos del Valle del Mantaro
INSERT INTO Distritos (nombre_distrito, provincia) VALUES
('Huancayo', 'Huancayo'),
('El Tambo', 'Huancayo'),
('Chilca', 'Huancayo'),
('Concepción', 'Concepción'),
('Chupaca', 'Chupaca'),
('Jauja', 'Jauja');

-- 2. Categorías Agrícolas
INSERT INTO Categorias (nombre_categoria) VALUES
('Tubérculos Andinos'),
('Granos y Cereales'),
('Hortalizas Frescas'),
('Lácteos Artesanales');

-- 3. Usuarios (Productores y Compradores)
INSERT INTO Usuarios (nombres, apellidos, dni, telefono, rol, id_distrito) VALUES
('Juan Carlos', 'Quispe Huamán', '41258963', '964112233', 'PRODUCTOR', 4), -- Concepción
('María Elena', 'Cárdenas Soto', '45871236', '964445566', 'PRODUCTOR', 5), -- Chupaca
('Restaurante El Olímpico', 'SAC', '20486123', '964778899', 'COMPRADOR', 1), -- Huancayo
('Luis Alberto', 'Mendoza Rojas', '71234568', '954123456', 'COMPRADOR', 2); -- El Tambo

-- 4. Catálogo de Productos
INSERT INTO Productos (nombre_producto, unidad_medida, id_categoria) VALUES
('Papa Huayro Seleccionada', 'Saco 50kg', 1),
('Quinua Blanca Orgánica', 'Kg', 2),
('Alcachofa Criolla', 'Docena', 3),
('Queso Fresco Andino', 'Molde 1kg', 4);

-- 5. Lotes de Cosecha Disponibles
INSERT INTO Lotes_Cosecha (id_productor, id_producto, precio_unitario, stock_disponible, fecha_cosecha, punto_entrega) VALUES
(1, 1, 85.00, 30.00, '2026-11-22', 'Feria Dominical Av. Huancavelica'),
(1, 2, 12.50, 150.00, '2026-11-20', 'Mercado Mayorista Ex-Maltería'),
(2, 4, 18.00, 45.00, '2026-11-23', 'Parque Constitución - Entrega Directa');
GO

-- Consulta de verificación (JOIN para demostrar la 3FN en tu exposición)
SELECT 
    l.id_lote,
    p.nombre_producto,
    c.nombre_categoria,
    u.nombres + ' ' + u.apellidos AS productor,
    d.nombre_distrito AS origen,
    l.precio_unitario,
    l.stock_disponible,
    l.punto_entrega
FROM Lotes_Cosecha l
INNER JOIN Productos p ON l.id_producto = p.id_producto
INNER JOIN Categorias c ON p.id_categoria = c.id_categoria
INNER JOIN Usuarios u ON l.id_productor = u.id_usuario
INNER JOIN Distritos d ON u.id_distrito = d.id_distrito;