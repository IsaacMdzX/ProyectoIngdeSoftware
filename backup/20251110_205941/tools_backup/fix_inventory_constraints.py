import os
import psycopg2
from psycopg2 import sql

dsn = os.environ.get('DATABASE_URL') or 'postgresql://admin:123456@localhost:5432/sneakers_store'
conn = psycopg2.connect(dsn)
conn.autocommit = False
cur = conn.cursor()
try:
    drops = [
        "ALTER TABLE stock.inventario DROP CONSTRAINT IF EXISTS fk_inventario_playera;",
        "ALTER TABLE stock.inventario DROP CONSTRAINT IF EXISTS fk_inventario_tenis;",
        "ALTER TABLE stock.inventario DROP CONSTRAINT IF EXISTS fk_inventario_gorra;",
    ]
    for s in drops:
        cur.execute(s)
        print('Executed:', s)
    # write rollback SQL
    rollback_sql = """
-- Rollback: recreate FK constraints (adjust schema/names if needed)
ALTER TABLE stock.inventario ADD CONSTRAINT fk_inventario_playera FOREIGN KEY (id_producto) REFERENCES productos.playeras(id_playera) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE stock.inventario ADD CONSTRAINT fk_inventario_tenis FOREIGN KEY (id_producto) REFERENCES productos.tenis(id_teni) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE stock.inventario ADD CONSTRAINT fk_inventario_gorra FOREIGN KEY (id_producto) REFERENCES productos.gorras(id_gorra) DEFERRABLE INITIALLY DEFERRED;
"""
    rb_path = os.path.join(os.path.dirname(__file__), '..', 'migrations', 'rollback_inventory_fks.sql')
    os.makedirs(os.path.dirname(rb_path), exist_ok=True)
    with open(rb_path, 'w') as f:
        f.write(rollback_sql)
    conn.commit()
    print('Constraints dropped. Rollback SQL written to', rb_path)
except Exception as e:
    conn.rollback()
    print('Error:', e)
finally:
    cur.close()
    conn.close()
