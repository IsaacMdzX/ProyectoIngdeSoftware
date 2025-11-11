import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from app.extensions import db
from app.public.models import Tenis, Playera, Gorra

app = create_app()

missing = []
referenced = set()
with app.app_context():
    static_dir = os.path.join(app.static_folder, 'images', 'product_images')
    # collect referenced filenames from all product tables
    for Model in (Tenis, Playera, Gorra):
        rows = db.session.execute(db.select(Model)).scalars().all()
        for r in rows:
            fn = getattr(r, 'image_filename', None)
            if fn:
                referenced.add(fn)
                path = os.path.join(static_dir, fn)
                if not os.path.exists(path):
                    missing.append((Model.__name__, getattr(r, 'id_teni', getattr(r, 'id_playera', getattr(r, 'id_gorra', None))), fn))

    print('Found', len(referenced), 'referenced image filenames across products')
    print('Missing files referenced in DB:', len(missing))
    for rec in missing[:50]:
        print(rec)

    # Set image_filename = NULL for missing files
    if missing:
        print('Nullifying missing image_filename references...')
        for model_name, id_val, fn in missing:
            if model_name == 'Tenis':
                obj = db.session.get(Tenis, id_val)
            elif model_name == 'Playera':
                obj = db.session.get(Playera, id_val)
            elif model_name == 'Gorra':
                obj = db.session.get(Gorra, id_val)
            else:
                obj = None
            if obj:
                obj.image_filename = None
        db.session.commit()
        print('DB updated: cleared', len(missing), 'references')

    # Move unreferenced files to backup
    all_files = [f for f in os.listdir(static_dir) if os.path.isfile(os.path.join(static_dir, f))]
    unreferenced = [f for f in all_files if f not in referenced]
    print('Total files in static dir:', len(all_files))
    print('Unreferenced files to move:', len(unreferenced))

    if unreferenced:
        ts = __import__('time').strftime('%Y%m%d_%H%M%S')
        backup_dir = os.path.join(os.path.dirname(__file__), '..', 'backup', ts, 'images')
        os.makedirs(backup_dir, exist_ok=True)
        for f in unreferenced:
            src = os.path.join(static_dir, f)
            dst = os.path.join(backup_dir, f)
            try:
                os.rename(src, dst)
            except Exception as e:
                print('Failed moving', src, '->', dst, e)
        print('Moved unreferenced files to', backup_dir)

    print('Done')
