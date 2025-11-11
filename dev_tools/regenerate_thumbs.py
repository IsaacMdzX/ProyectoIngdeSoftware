import os
from app import create_app
from app.extensions import db
from app.public.models import Tenis, Playera, Gorra

try:
    from PIL import Image
    HAS_PIL = True
except Exception:
    HAS_PIL = False

app = create_app()

with app.app_context():
    if not HAS_PIL:
        print('Pillow no está disponible en este intérprete. Instala Pillow en el venv y vuelve a ejecutar.')
        raise SystemExit(1)

    static_root = app.static_folder
    upload_dir = os.path.join(static_root, 'images', 'product_images')
    small_dir = os.path.join(upload_dir, 'thumbs', 'small')
    medium_dir = os.path.join(upload_dir, 'thumbs', 'medium')
    os.makedirs(small_dir, exist_ok=True)
    os.makedirs(medium_dir, exist_ok=True)

    def ensure_thumb(filename):
        if not filename:
            return 'no_filename'
        orig = os.path.join(upload_dir, filename)
        small = os.path.join(small_dir, filename)
        medium = os.path.join(medium_dir, filename)
        status = []
        if not os.path.exists(orig):
            status.append('missing_original')
            return ','.join(status)
        try:
            if not os.path.exists(small):
                with Image.open(orig) as im:
                    im_copy = im.copy()
                    im_copy.thumbnail((150, 150))
                    im_copy.save(small, quality=85)
                status.append('created_small')
            else:
                status.append('small_ok')
            if not os.path.exists(medium):
                with Image.open(orig) as im2:
                    im2_copy = im2.copy()
                    im2_copy.thumbnail((800, 800))
                    im2_copy.save(medium, quality=85)
                status.append('created_medium')
            else:
                status.append('medium_ok')
        except Exception as e:
            status.append('error:'+str(e))
        return ','.join(status)

    total = 0
    changes = []
    for model, name in ((Tenis, 'Tenis'), (Playera, 'Playera'), (Gorra, 'Gorra')):
        rows = db.session.execute(db.select(model)).scalars().all()
        for r in rows:
            total += 1
            fn = getattr(r, 'image_filename', None)
            res = ensure_thumb(fn)
            if res and (res.startswith('created') or 'created' in res or 'missing_original' in res or res.startswith('error')):
                changes.append((name, getattr(r, 'id_teni', getattr(r, 'id_playera', getattr(r, 'id_gorra', None))), fn, res))

    print('Processed products:', total)
    if changes:
        print('Changes / issues:')
        for c in changes:
            print(' -', c)
    else:
        print('No changes needed; all thumbs present.')
