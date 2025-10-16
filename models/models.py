from flask_sqlalchemy import SQLAlchemy
from database import get_db_connection  # Manteniendo tu conexión actual

db = SQLAlchemy()

class Usuario:
    @staticmethod
    def login(email, password):
        """Verificar usuario y contraseña"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM usuarios.admin WHERE correo = %s AND contrasena = %s"
        cursor.execute(query, (email, password))
        usuario = cursor.fetchone()
        
        cursor.close()
        conn.close()
        return usuario

    @staticmethod
    def es_admin(user_id):
        """Verificar si un usuario es administrador"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM usuarios.admin WHERE id_admin = %s"
        cursor.execute(query, (user_id,))
        admin = cursor.fetchone()
        
        cursor.close()
        conn.close()
        return admin is not None

class Cliente:
    @staticmethod
    def obtener_todos():
        """Obtener todos los clientes"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM usuarios.cliente"
        cursor.execute(query)
        clientes = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return clientes
    
    @staticmethod
    def crear(nombre, email, telefono):
        """Crear nuevo cliente"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "INSERT INTO usuarios.cliente (nombre, email, telefono) VALUES (%s, %s, %s)"
        cursor.execute(query, (nombre, email, telefono))
        conn.commit()
        
        cursor.close()
        conn.close()
        return True

# Modelos SQLAlchemy para compatibilidad con el panel admin
class AdminUser(db.Model):
    __tablename__ = 'admin'
    __table_args__ = {'schema': 'usuarios'}
    
    id_admin = db.Column('id_admin', db.Integer, primary_key=True)
    nombre_admin = db.Column('nombre_admin', db.String(100))
    correo = db.Column('correo', db.String(120))
    telefono = db.Column('telefono', db.String(20))
    contrasena = db.Column('contrasena', db.String(200))
    
    @property
    def es_admin(self):
        return True  # Todos los usuarios de esta tabla son admins
    
    @property
    def username(self):
        return self.nombre_admin
    
    @property
    def email(self):
        return self.correo
    
    @property
    def password(self):
        return self.contrasena
    
    def check_password(self, password):
        """Verificar contraseña (adaptada a tu estructura)"""
        return self.contrasena == password  # Para desarrollo

class ClienteUser(db.Model):
    __tablename__ = 'cliente'
    __table_args__ = {'schema': 'usuarios'}
    
    # Define aquí las columnas de tu tabla cliente si las necesitas
    id_cliente = db.Column('id_cliente', db.Integer, primary_key=True)
    nombre = db.Column('nombre', db.String(100))
    email = db.Column('email', db.String(120))
    telefono = db.Column('telefono', db.String(20))
    
    @property
    def es_admin(self):
        return False  # Los clientes no son admins