from database import get_db_connection

class Usuario:
    @staticmethod
    def login(email, password):
        """Ejemplo: Verificar usuario y contraseña"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM usuarios WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))
        usuario = cursor.fetchone()
        
        cursor.close()
        conn.close()
        return usuario

class Cliente:
    @staticmethod
    def obtener_todos():
        """Ejemplo: Obtener todos los clientes"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM clientes"
        cursor.execute(query)
        clientes = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return clientes
    
    @staticmethod
    def crear(nombre, email, telefono):
        """Ejemplo: Crear nuevo cliente"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "INSERT INTO clientes (nombre, email, telefono) VALUES (%s, %s, %s)"
        cursor.execute(query, (nombre, email, telefono))
        conn.commit()
        
        cursor.close()
        conn.close()
        return True
    
    