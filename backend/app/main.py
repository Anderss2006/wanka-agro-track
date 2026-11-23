from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.database import get_db_connection
from app.schemas import LoteCreate, PedidoCreate

app = FastAPI(
    title="WankaAgro Track API",
    description="API de trazabilidad y comercio justo para el Valle del Mantaro - Huancayo",
    version="1.0.0"
)

# Permitir que el Frontend (HTML/JS) se comunique con este Backend sin bloqueos CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/lotes", tags=["Ofertas Agrícolas"])
def listar_lotes_disponibles():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT 
            l.id_lote, p.nombre_producto, p.unidad_medida, c.nombre_categoria,
            u.nombres + ' ' + u.apellidos AS productor, u.telefono,
            d.nombre_distrito AS origen, l.precio_unitario, 
            l.stock_disponible, l.fecha_cosecha, l.punto_entrega
        FROM Lotes_Cosecha l
        INNER JOIN Productos p ON l.id_producto = p.id_producto
        INNER JOIN Categorias c ON p.id_categoria = c.id_categoria
        INNER JOIN Usuarios u ON l.id_productor = u.id_usuario
        INNER JOIN Distritos d ON u.id_distrito = d.id_distrito
        WHERE l.estado = 'DISPONIBLE' AND l.stock_disponible > 0
        ORDER BY l.id_lote DESC
    """
    cursor.execute(query)
    columnas = [column[0] for column in cursor.description]
    resultados = [dict(zip(columnas, row)) for row in cursor.fetchall()]
    conn.close()
    return resultados

@app.get("/api/catalogos", tags=["Datos Maestros"])
def obtener_catalogos():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id_usuario, nombres + ' ' + apellidos AS nombre FROM Usuarios WHERE rol = 'PRODUCTOR'")
    productores = [{"id": r[0], "nombre": r[1]} for r in cursor.fetchall()]
    
    cursor.execute("SELECT id_usuario, nombres + ' ' + apellidos AS nombre FROM Usuarios WHERE rol = 'COMPRADOR'")
    compradores = [{"id": r[0], "nombre": r[1]} for r in cursor.fetchall()]
    
    cursor.execute("SELECT id_producto, nombre_producto + ' (' + unidad_medida + ')' AS nombre FROM Productos")
    productos = [{"id": r[0], "nombre": r[1]} for r in cursor.fetchall()]
    
    conn.close()
    return {"productores": productores, "compradores": compradores, "productos": productos}

@app.post("/api/lotes", tags=["Ofertas Agrícolas"], status_code=201)
def publicar_lote(lote: LoteCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO Lotes_Cosecha (id_productor, id_producto, precio_unitario, stock_disponible, fecha_cosecha, punto_entrega)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (
            lote.id_productor, lote.id_producto, lote.precio_unitario,
            lote.stock_disponible, lote.fecha_cosecha, lote.punto_entrega
        ))
        conn.commit()
        return {"mensaje": "Lote de cosecha publicado exitosamente"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Error al registrar lote: {str(e)}")
    finally:
        conn.close()

@app.post("/api/pedidos", tags=["Reservas y Ventas"], status_code=201)
def registrar_pedido(pedido: PedidoCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 1. Verificar stock y obtener precio actual del lote
        cursor.execute("SELECT precio_unitario, stock_disponible FROM Lotes_Cosecha WHERE id_lote = ?", (pedido.id_lote,))
        lote = cursor.fetchone()
        if not lote:
            raise HTTPException(status_code=404, detail="El lote seleccionado no existe")
        
        precio_actual, stock_actual = float(lote[0]), float(lote[1])
        if pedido.cantidad > stock_actual:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente. Solo quedan {stock_actual} unidades.")

        # 2. Insertar cabecera del pedido y recuperar su ID generado (SCOPE_IDENTITY)
        cursor.execute("INSERT INTO Pedidos (id_comprador) OUTPUT INSERTED.id_pedido VALUES (?)", (pedido.id_comprador,))
        id_pedido_nuevo = cursor.fetchone()[0]

        # 3. Insertar detalle con el precio histórico pactado
        cursor.execute(
            "INSERT INTO Detalle_Pedidos (id_pedido, id_lote, cantidad, precio_pactado) VALUES (?, ?, ?, ?)",
            (id_pedido_nuevo, pedido.id_lote, pedido.cantidad, precio_actual)
        )

        # 4. Actualizar stock y cambiar estado si llega a 0
        nuevo_stock = stock_actual - pedido.cantidad
        nuevo_estado = 'AGOTADO' if nuevo_stock == 0 else 'DISPONIBLE'
        cursor.execute(
            "UPDATE Lotes_Cosecha SET stock_disponible = ?, estado = ? WHERE id_lote = ?",
            (nuevo_stock, nuevo_estado, pedido.id_lote)
        )

        conn.commit()
        return {"mensaje": "Reserva confirmada y stock actualizado", "id_pedido": id_pedido_nuevo}
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error en la transacción: {str(e)}")
    finally:
        conn.close()