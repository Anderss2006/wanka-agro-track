from fastapi import HTTPException
from app.database import get_db_connection
from app.schemas.lote import LoteCreate
from app.schemas.productor import ProductorCreate


def listar_lotes_disponibles():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT 
            l.id_lote,
            p.nombre_producto,
            p.unidad_medida,
            c.nombre_categoria,
            u.nombres + ' ' + u.apellidos AS productor,
            u.telefono,
            d.nombre_distrito + ' (' + d.provincia + ')' AS origen,
            l.precio_unitario,
            l.stock_disponible,
            CONVERT(VARCHAR(10), l.fecha_cosecha, 23) AS fecha_cosecha,
            l.punto_entrega
        FROM Lotes_Cosecha l
        INNER JOIN Productos p ON l.id_producto = p.id_producto
        INNER JOIN Categorias c ON p.id_categoria = c.id_categoria
        INNER JOIN Usuarios u ON l.id_productor = u.id_usuario
        INNER JOIN Distritos d ON u.id_distrito = d.id_distrito
        WHERE l.estado = 'DISPONIBLE' AND l.stock_disponible > 0
        ORDER BY l.fecha_cosecha DESC
    """
    cursor.execute(query)
    columnas = [column[0] for column in cursor.description]
    resultados = [dict(zip(columnas, row)) for row in cursor.fetchall()]
    conn.close()
    return resultados


def obtener_catalogos():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id_usuario, nombres + ' ' + apellidos AS nombre FROM Usuarios WHERE rol = 'PRODUCTOR'")
    productores = [{"id": r[0], "nombre": r[1]} for r in cursor.fetchall()]

    cursor.execute("SELECT id_usuario, nombres + ' ' + apellidos AS nombre FROM Usuarios WHERE rol = 'COMPRADOR'")
    compradores = [{"id": r[0], "nombre": r[1]} for r in cursor.fetchall()]

    cursor.execute("SELECT id_producto, nombre_producto + ' (' + unidad_medida + ')' AS nombre FROM Productos")
    productos = [{"id": r[0], "nombre": r[1]} for r in cursor.fetchall()]

    cursor.execute("SELECT id_distrito, nombre_distrito + ' (' + provincia + ')' AS nombre FROM Distritos")
    distritos = [{"id": r[0], "nombre": r[1]} for r in cursor.fetchall()]

    conn.close()
    return {
        "productores": productores,
        "compradores": compradores,
        "productos": productos,
        "distritos": distritos
    }


def publicar_lote(lote: LoteCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO Lotes_Cosecha (id_productor, id_producto, precio_unitario, stock_disponible, fecha_cosecha, punto_entrega, estado)
            VALUES (?, ?, ?, ?, ?, ?, 'DISPONIBLE')
        """
        cursor.execute(query, (
            lote.id_productor,
            lote.id_producto,
            lote.precio_unitario,
            lote.stock_disponible,
            lote.fecha_cosecha,
            lote.punto_entrega
        ))
        conn.commit()
        return {"mensaje": "Cosecha publicada con éxito en el catálogo."}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al publicar el lote: {str(e)}")
    finally:
        conn.close()


def registrar_productor(productor: ProductorCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_usuario FROM Usuarios WHERE dni = ?", (productor.dni,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Ya existe un usuario registrado con ese número de DNI.")

        query = """
            INSERT INTO Usuarios (nombres, apellidos, dni, telefono, rol, id_distrito)
            VALUES (?, ?, ?, ?, 'PRODUCTOR', ?)
        """
        cursor.execute(query, (
            productor.nombres.strip(),
            productor.apellidos.strip(),
            productor.dni,
            productor.telefono,
            productor.id_distrito
        ))
        conn.commit()
        return {"mensaje": f"¡Bienvenido a WankaAgro Track, {productor.nombres}! Ya puedes publicar tus cosechas."}
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al registrar productor: {str(e)}")
    finally:
        conn.close()