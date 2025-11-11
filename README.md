Proyecto Tr.sneakers — instrucciones rápidas

Este README contiene pasos mínimos para poner en marcha la aplicación en desarrollo, ejecutar pruebas básicas de subida de imágenes y dónde encontrar los backups/rollbacks que se generaron.

Requisitos
- Linux / macOS / Windows con Python 3.12
- PostgreSQL accesible con las credenciales configuradas en `config/config.py` o la variable `DATABASE_URL`.

Instalación y ejecución (desarrollo)

1) Activar entorno virtual (desde la raíz del proyecto):

```bash
source venv/bin/activate
```

2) Instalar dependencias (si aún no lo hiciste):

```bash
pip install -r Requeriments.txt
```

3) Variables de entorno importantes
- `DATABASE_URL` (opcional) — si quieres usar otra DB.
- `MP_ACCESS_TOKEN` — token de Mercado Pago si vas a probar pagos (ten cuidado en entorno de producción).

4) Iniciar la aplicación (dev server):

```bash
# desde la raíz del proyecto
./venv/bin/python run.py
# o
export FLASK_APP=run.py
flask run
```

5) Probar la UI
- Entra en `http://127.0.0.1:5000` (o la IP/puerto que aparezca en la salida). 
- Loguea como administrador y abre `http://127.0.0.1:5000/agregar-producto` para subir una imagen y crear un producto.

Notas sobre imágenes
- Las imágenes subidas se guardan en `app/static/images/product_images/`.
- Miniaturas se generan en `app/static/images/product_images/thumbs/small/` y `.../thumbs/medium/`.
- Si no ves miniaturas, instala las dependencias (especialmente `Pillow`) y vuelve a intentar.

Backups y rollback
- Durante las tareas recientes se generaron backups automáticos en la carpeta `backup/` con timestamp.
- El script que eliminó las constraints FK conflictivas dejó un SQL de rollback en `migrations/rollback_inventory_fks.sql`.

Limpieza y diagnósticos
- Temporales y scripts de diagnóstico que se usaron están en `backup/<timestamp>/tools/` — no los borré del backup por seguridad.
- Si quieres que limpie más (eliminar backups o eliminar archivos de prueba), dime y lo hago con un backup previo.

Soporte de pago (Mercado Pago)
- El proyecto usa la SDK `mercadopago` (ya incluida en `Requeriments.txt`).
- Ejecuta la app desde el venv para asegurarte de que la SDK está disponible.
- Evita usar tokens productivos en entornos no seguros. Para pruebas, usa `sandbox` cuando sea posible.

Contacto rápido
- Si quieres que deje el repo aún más "limpio" (borrar backups, crear migraciones formales, o añadir tests), dime qué prefieres y lo implemento.
