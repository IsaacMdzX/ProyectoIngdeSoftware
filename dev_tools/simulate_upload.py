import osimport io

from app import create_appimport os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = create_app()from PIL import Image

from app import create_app

with app.test_client() as c:from app.extensions import db

    # set admin sessionfrom app.public.models import Marca, TipoProducto, TallaCalzado, Tenis

    with c.session_transaction() as sess:

        sess['role'] = 'admin'app = create_app()

        sess['user_id'] = 1

with app.app_context():

    # pick an existing image to re-upload as test (use an existing file in product_images)    # Ensure at least one Marca and TipoProducto exist

    static_root = app.static_folder    marca = db.session.execute(db.select(Marca)).scalars().first()

    upload_dir = os.path.join(static_root, 'images', 'product_images')    if not marca:

    src_file = None        marca = Marca(nombre_marca='MarcaTest')

    for f in os.listdir(upload_dir):        db.session.add(marca)

        if f.endswith('.jpg') or f.endswith('.jpeg') or f.endswith('.png'):        db.session.commit()

            # skip thumbs directory

            if f == 'thumbs':    tipo = db.session.execute(db.select(TipoProducto)).scalars().first()

                continue    if not tipo:

            src_file = os.path.join(upload_dir, f)        tipo = TipoProducto(nombre_tipo='TipoTest')

            break        db.session.add(tipo)

    if not src_file:        db.session.commit()

        print('No source image found to upload.')

    else:    talla = db.session.execute(db.select(TallaCalzado)).scalars().first()

        print('Using source file:', src_file)    # talla is optional; if exists use id, else None

        data = {    talla_id = getattr(talla, 'id_talla_calzado', None) if talla else None

            'categoria': 'gorra',

            'nombre': 'Test Upload Gorra',    client = app.test_client()

            'precio': '199',    # Set session to admin

            'cantidad': '5'    with client.session_transaction() as sess:

        }        sess['role'] = 'admin'

        with open(src_file, 'rb') as img:

            data['imagen'] = (img, os.path.basename(src_file))    # Create an in-memory image

            resp = c.post('/agregar-producto', data=data, content_type='multipart/form-data', follow_redirects=True)    img = Image.new('RGB', (1000, 600), (10, 120, 200))

            print('POST /agregar-producto ->', resp.status_code)    bio = io.BytesIO()

            text = resp.get_data(as_text=True)    img.save(bio, format='JPEG')

            # print small snippet and check for flash messages    bio.seek(0)

            print(text[:800])

    data = {

        # inspect thumbs folder for new file(s)        'categoria': 'tenis',

        small_dir = os.path.join(upload_dir, 'thumbs', 'small')        'nombre': 'Autotest Tenis',

        medium_dir = os.path.join(upload_dir, 'thumbs', 'medium')        'marca': str(marca.id_marca),

        print('\nSmall thumbs files:')        'tipo': str(tipo.id_tipo_producto),

        if os.path.exists(small_dir):        'precio': '79.99',

            for f in os.listdir(small_dir):        'cantidad': '5'

                print(' -', f)    }

        print('\nMedium thumbs files:')    if talla_id:

        if os.path.exists(medium_dir):        data['talla_calzado'] = str(talla_id)

            for f in os.listdir(medium_dir):

                print(' -', f)    # files: field name 'imagen'

    data_files = {
        'imagen': (bio, 'autotest.jpg')
    }

    print('Enviando POST a /agregar-producto ...')
    resp = client.post('/agregar-producto', data={**data, 'imagen': (bio, 'autotest.jpg')}, content_type='multipart/form-data', follow_redirects=True)

    print('Código HTTP:', resp.status_code)
    # Save response for debugging
    text = resp.get_data(as_text=True)
    if resp.status_code == 200 and 'Producto (tenis) agregado exitosamente.' in text:
        print('Respuesta indica éxito. Buscando el producto en DB...')
        producto = db.session.execute(db.select(Tenis).where(Tenis.nombre_tenis == 'Autotest Tenis')).scalars().first()
        # Check all product tables for the created name
        import os
        found = False
        tenis_prod = db.session.execute(db.select(Tenis).where(Tenis.nombre_tenis == 'Autotest Tenis')).scalars().first()
        if tenis_prod:
            found = True
            print('Tenis creado. id:', tenis_prod.id_teni, 'image_filename:', tenis_prod.image_filename)
            filename = tenis_prod.image_filename
        else:
            # check playeras and gorras by similar name
            from app.public.models import Playera, Gorra
            playera_prod = db.session.execute(db.select(Playera).where(Playera.nombre_playera == 'Autotest Tenis')).scalars().first()
            gorra_prod = db.session.execute(db.select(Gorra).where(Gorra.nombre_gorra == 'Autotest Tenis')).scalars().first()
            if playera_prod:
                found = True
                print('Playera creada (unexpected). id:', playera_prod.id_playera, 'image_filename:', playera_prod.image_filename)
                filename = playera_prod.image_filename
            elif gorra_prod:
                found = True
                print('Gorra creada (unexpected). id:', gorra_prod.id_gorra, 'image_filename:', gorra_prod.image_filename)
                filename = gorra_prod.image_filename
            else:
                filename = None

        if found and filename:
            static_img_dir = os.path.join(app.static_folder, 'images', 'product_images')
            orig = os.path.join(static_img_dir, filename)
            small = os.path.join(static_img_dir, 'thumbs', 'small', filename)
            medium = os.path.join(static_img_dir, 'thumbs', 'medium', filename)
            print('Paths:')
            print(' original:', orig, 'exists:', os.path.exists(orig))
            print(' small:', small, 'exists:', os.path.exists(small))
            print(' medium:', medium, 'exists:', os.path.exists(medium))
        else:
            print('No se encontró el producto en ninguna tabla.')
    else:
        print('Respuesta no indica éxito. Texto de respuesta (completo, truncado a 8000 chars):')
        print(text[:8000])

        # Try again with category 'playera' in case DB enforces playera FK
        bio.seek(0)
        data2 = data.copy()
        data2['categoria'] = 'playera'
        data2['nombre'] = 'Autotest Playera'
        print('\nIntentando POST con categoria=playera ...')
        resp2 = client.post('/agregar-producto', data={**data2, 'imagen': (bio, 'autotest2.jpg')}, content_type='multipart/form-data', follow_redirects=True)
        print('Código HTTP (playera):', resp2.status_code)
        txt2 = resp2.get_data(as_text=True)
        if resp2.status_code == 200 and 'Producto (playera) agregado exitosamente.' in txt2:
            print('Playera creada correctamente según respuesta.')
            from app.public.models import Playera
            p = db.session.execute(db.select(Playera).where(Playera.nombre_playera == 'Autotest Playera')).scalars().first()
            if p:
                print('Playera en DB id:', p.id_playera, 'image_filename:', p.image_filename)
                static_img_dir = os.path.join(app.static_folder, 'images', 'product_images')
                orig = os.path.join(static_img_dir, p.image_filename) if p.image_filename else None
                small = os.path.join(static_img_dir, 'thumbs', 'small', p.image_filename) if p.image_filename else None
                medium = os.path.join(static_img_dir, 'thumbs', 'medium', p.image_filename) if p.image_filename else None
                print('Paths exist: orig', os.path.exists(orig) if orig else 'N/A', 'small', os.path.exists(small) if small else 'N/A', 'medium', os.path.exists(medium) if medium else 'N/A')
            else:
                print('No se encontró playera en DB tras respuesta positiva.')
        else:
            print('Respuesta playera (trunc):')
            print(txt2[:2000])

    # close streams
    bio.close()
