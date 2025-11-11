import os
from app import create_app
from app.extensions import db
from app.public.models import Tenis, Playera, Gorra

app = create_app()

with app.app_context():
    static_root = app.static_folder
    upload_dir = os.path.join(static_root, 'images', 'product_images')
    print('Static root:', static_root)
    print('Upload dir:', upload_dir)
    print('\n--- Tenis ---')
    tenis = db.session.execute(db.select(Tenis)).scalars().all()
    for t in tenis:
        fn = getattr(t, 'image_filename', None)
        orig = os.path.join(upload_dir, fn) if fn else None
        small = os.path.join(upload_dir, 'thumbs', 'small', fn) if fn else None
        med = os.path.join(upload_dir, 'thumbs', 'medium', fn) if fn else None
        print(f'id={t.id_teni!s:5} name={t.nombre_tenis!s:30} image={fn!s:30} exists_orig={os.path.exists(orig) if orig else False} small={os.path.exists(small) if small else False} med={os.path.exists(med) if med else False}')

    print('\n--- Playeras ---')
    playeras = db.session.execute(db.select(Playera)).scalars().all()
    for p in playeras:
        fn = getattr(p, 'image_filename', None)
        orig = os.path.join(upload_dir, fn) if fn else None
        small = os.path.join(upload_dir, 'thumbs', 'small', fn) if fn else None
        med = os.path.join(upload_dir, 'thumbs', 'medium', fn) if fn else None
        print(f'id={p.id_playera!s:5} name={p.nombre_playera!s:30} image={fn!s:30} exists_orig={os.path.exists(orig) if orig else False} small={os.path.exists(small) if small else False} med={os.path.exists(med) if med else False}')

    print('\n--- Gorras ---')
    gorras = db.session.execute(db.select(Gorra)).scalars().all()
    for g in gorras:
        fn = getattr(g, 'image_filename', None)
        orig = os.path.join(upload_dir, fn) if fn else None
        small = os.path.join(upload_dir, 'thumbs', 'small', fn) if fn else None
        med = os.path.join(upload_dir, 'thumbs', 'medium', fn) if fn else None
        print(f'id={g.id_gorra!s:5} name={g.nombre_gorra!s:30} image={fn!s:30} exists_orig={os.path.exists(orig) if orig else False} small={os.path.exists(small) if small else False} med={os.path.exists(med) if med else False}')

    # list files in upload_dir
    print('\nFiles in product_images:')
    try:
        for f in os.listdir(upload_dir):
            print(' -', f)
    except Exception as e:
        print('Cannot list upload dir:', e)
