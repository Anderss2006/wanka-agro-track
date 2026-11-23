from fastapi import HTTPException
from app.database import get_db_connection
from app.schemas.pedido import PedidoCreate


def crear_pedido(pedido: PedidoCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 1. Verificar stock y precio actual del lote
        cursor.execute(
            "SELECT stock_disponible, precio_unitario, estado FROM Lotes_Cosecha WHERE id_lote = ?",
            (pedido.id_lote,)
        )
        lote = cursor.fetchone()

        if not lote:
            raise HTTPException(status_code=404, detail="El lote seleccionado no existe.")

        stock_actual = float(lote[0])
        precio_unitario = float(lote[1])
        estado = lote[2]
        cantidad_pedida = float(pedido.cantidad)

        if estado != "DISPONIBLE" or stock_actual < cantidad_pedida:
            raise HTTPException(status_code=400, detail="Stock insuficiente para completar la reserva.")

        # 2. Insertar cabecera en Pedidos y obtener id_pedido
        cursor.execute(
            """
            INSERT INTO Pedidos (id_comprador, fecha_pedido, estado_pedido)
            OUTPUT INSERTED.id_pedido
            VALUES (?, GETDATE(), 'PENDIENTE')
            """,
            (pedido.id_comprador,)
        )
        id_pedido = cursor.fetchone()[0]

        # 3. Insertar detalle en Detalle_Pedidos
        cursor.execute(
            """
            INSERT INTO Detalle_Pedidos (id_pedido, id_lote, cantidad, precio_pactado)
            VALUES (?, ?, ?, ?)
            """,
            (id_pedido, pedido.id_lote, cantidad_pedida, precio_unitario)
        )

        # 4. Descontar stock del lote
        nuevo_stock = stock_actual - cantidad_pedida
        nuevo_estado = "AGOTADO" if nuevo_stock == 0 else "DISPONIBLE"
        cursor.execute(
            "UPDATE Lotes_Cosecha SET stock_disponible = ?, estado = ? WHERE id_lote = ?",
            (nuevo_stock, nuevo_estado, pedido.id_lote)
        )

        conn.commit()
        return {"mensaje": "Reserva confirmada con éxito.", "id_pedido": id_pedido}

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al procesar la reserva: {str(e)}")
    finally:
        conn.close()


def listar_pedidos_usuario(id_usuario: int, rol: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        filtro = "WHERE l.id_productor = ?" if rol.upper() == "PRODUCTOR" else "WHERE ped.id_comprador = ?"

        query = f"""
            SELECT 
                ped.id_pedido,
                CONVERT(VARCHAR(16), ped.fecha_pedido, 120) AS fecha_pedido,
                prod.nombre_producto,
                prod.unidad_medida,
                det.cantidad,
                det.precio_pactado AS precio_unitario,
                (det.cantidad * det.precio_pactado) AS total_pagar,
                ped.estado_pedido AS estado,
                l.punto_entrega,
                u_prod.nombres + ' ' + u_prod.apellidos AS productor,
                u_prod.telefono AS telefono_productor,
                u_comp.nombres + ' ' + u_comp.apellidos AS comprador,
                u_comp.telefono AS telefono_comprador
            FROM Pedidos ped
            INNER JOIN Detalle_Pedidos det ON ped.id_pedido = det.id_pedido
            INNER JOIN Lotes_Cosecha l ON det.id_lote = l.id_lote
            INNER JOIN Productos prod ON l.id_producto = prod.id_producto
            INNER JOIN Usuarios u_prod ON l.id_productor = u_prod.id_usuario
            INNER JOIN Usuarios u_comp ON ped.id_comprador = u_comp.id_usuario
            {filtro}
            ORDER BY ped.id_pedido DESC
        """
        cursor.execute(query, (id_usuario,))
        columnas = [column[0] for column in cursor.description]
        return [dict(zip(columnas, row)) for row in cursor.fetchall()]
    finally:
        conn.close()