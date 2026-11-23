from fastapi import HTTPException
from app.database import get_db_connection
from app.schemas.auth import LoginRequest

def autenticar_usuario(datos: LoginRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            SELECT 
                u.id_usuario,
                u.nombres,
                u.apellidos,
                u.dni,
                u.telefono,
                u.rol,
                d.nombre_distrito + ' (' + d.provincia + ')' AS distrito
            FROM Usuarios u
            INNER JOIN Distritos d ON u.id_distrito = d.id_distrito
            WHERE u.dni = ? AND u.telefono = ?
        """
        cursor.execute(query, (datos.dni.strip(), datos.clave.strip()))
        row = cursor.fetchone()

        if not row:
            raise HTTPException(
                status_code=401,
                detail="DNI o celular/clave incorrectos. Verifica tus datos registrados."
            )

        return {
            "mensaje": f"Bienvenido, {row[1]} {row[2]}",
            "usuario": {
                "id_usuario": row[0],
                "nombres": row[1],
                "apellidos": row[2],
                "nombre_completo": f"{row[1]} {row[2]}",
                "dni": row[3],
                "telefono": row[4],
                "rol": row[5],
                "distrito": row[6]
            }
        }
    finally:
        conn.close()