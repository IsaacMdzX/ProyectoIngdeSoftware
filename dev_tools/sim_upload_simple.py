import os
from app import create_app

app = create_app()

with app.test_client() as client:
    # set admin session
    with client.session_transaction() as sess:
        sess['role'] = 'admin'
        sess['user_id'] = 1

    static_root = app.static_folder
    upload_dir = os.path.join(static_root, 'images', 'product_images')
    src_file = None
    for f in os.listdir(upload_dir):
        if f in ('thumbs',):
            continue
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            src_file = os.path.join(upload_dir, f)
            break
    if not src_file:
        print('No source file found in', upload_dir)
    else:
        print('Using source file:', src_file)
        data = {
            'categoria': 'gorra',
            'nombre': 'Sim Test Gorra',
            'precio': '99.9',
            'cantidad': '2'
        }
        with open(src_file, 'rb') as img:
            data['imagen'] = (img, os.path.basename(src_file))
            resp = client.post('/agregar-producto', data=data, content_type='multipart/form-data', follow_redirects=True)
            print('POST status:', resp.status_code)
            text = resp.get_data(as_text=True)
            print('Response snippet:\n', text[:800])

        small_dir = os.path.join(upload_dir, 'thumbs', 'small')
        medium_dir = os.path.join(upload_dir, 'thumbs', 'medium')
        print('\nSmall thumbs:')
        if os.path.exists(small_dir):
            for f in os.listdir(small_dir):
                print(' -', f)
        print('\nMedium thumbs:')
        if os.path.exists(medium_dir):
            for f in os.listdir(medium_dir):
                print(' -', f)
