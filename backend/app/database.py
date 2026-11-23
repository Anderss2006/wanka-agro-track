import pyodbc

# Cadena de conexión exacta para tu instancia SQL Server 2025 Express
CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS01;"
    "DATABASE=WankaAgroDB;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

def get_db_connection():
    conn = pyodbc.connect(CONN_STR)
    return conn