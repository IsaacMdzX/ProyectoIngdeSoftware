from app import create_app
from database import db

app = create_app()

def init_db():
    with app.app_context():
        print('Creando tablas en la base de datos...')
        uri = app.config.get('SQLALCHEMY_DATABASE_URI', '') or ''
        # Si estamos usando SQLite en desarrollo, muchos modelos usan schemas
        # (ej. 'productos', 'usuarios') que SQLite no soporta. Para permitir
        # pruebas locales, eliminamos temporalmente el esquema de las tablas
        # en la metadata antes de crear las tablas.
        if uri.startswith('sqlite'):
            for table in list(db.metadata.tables.values()):
                # quitar schema si existe
                if getattr(table, 'schema', None):
                    table.schema = None

        db.create_all()
        print('Tablas creadas (si la conexión y permisos son correctos).')

if __name__ == '__main__':
    init_db()
