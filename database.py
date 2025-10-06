import psycopg2

def get_db_connection():
    # Configuración DUPLICADA en cada archivo
    return psycopg2.connect(
        host='localhost',      # ← Mismo dato en varios archivos
        user='postgres',       # ← Mismo dato en varios archivos
        password='password',   # ← Mismo dato en varios archivos
        database='parqueo_db'  # ← Mismo dato en varios archivos
    )