import psycopg2
import os

dsn = os.environ.get('DATABASE_URL') or 'postgresql://admin:123456@localhost:5432/sneakers_store'
conn = psycopg2.connect(dsn)
cur = conn.cursor()
cur.execute("SELECT conname, pg_get_constraintdef(c.oid) FROM pg_constraint c WHERE c.conrelid = 'stock.inventario'::regclass;")
rows = cur.fetchall()
if not rows:
    print('No constraints found on stock.inventario')
else:
    for name, defn in rows:
        print('CONSTRAINT:', name)
        print(defn)
        print('---')
cur.close()
conn.close()
