import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from app.extensions import db
from app.public.models import Tenis, Playera, Gorra

app = create_app()

with app.app_context():
    # 1) Remove products with names starting with 'Autotest'
    removed = 0
    for Model, name_col in ((Tenis, 'nombre_tenis'), (Playera, 'nombre_playera'), (Gorra, 'nombre_gorra')):
        q = db.select(Model).where(getattr(Model, name_col).ilike('Autotest%'))
        rows = db.session.execute(q).scalars().all()
        for r in rows:
            # delete related inventory entries
            try:
                db.session.execute(db.delete(db.inspect(db.session.bind).tables.get('stock.inventario')))
            except Exception:
                pass
            db.session.delete(r)
            removed += 1
    if removed:
        db.session.commit()
    print('Removed autotest products:', removed)

    # 2) Regenerate missing thumbnails for products that have image_filename but missing thumbs
    static_dir = os.path.join(app.static_folder, 'images', 'product_images')
    small_dir = os.path.join(static_dir, 'thumbs', 'small')
    med_dir = os.path.join(static_dir, 'thumbs', 'medium')
    os.makedirs(small_dir, exist_ok=True)
    os.makedirs(med_dir, exist_ok=True)

    try:
        from PIL import Image
        HAS_PIL = True
    except Exception:
        HAS_PIL = False

    regenerated = 0
    for Model in (Tenis, Playera, Gorra):
        rows = db.session.execute(db.select(Model)).scalars().all()
        for r in rows:
            fn = getattr(r, 'image_filename', None)
            if not fn:
                continue
            orig = os.path.join(static_dir, fn)
            small = os.path.join(small_dir, fn)
            medium = os.path.join(med_dir, fn)
            if not os.path.exists(orig):
                print('Original missing for', fn)
                continue
            if os.path.exists(small) and os.path.exists(medium):
                continue
            if not HAS_PIL:
                print('Pillow not installed; cannot regenerate', fn)
                continue
            try:
                with Image.open(orig) as im:
                    im_copy = im.copy()
                    im_copy.thumbnail((150,150))
                    im_copy.save(small, quality=85)
                with Image.open(orig) as im2:
                    im2_copy = im2.copy()
                    im2_copy.thumbnail((800,800))
                    im2_copy.save(medium, quality=85)
                regenerated += 1
            except Exception as e:
                print('Failed regenerating for', fn, e)
    print('Regenerated thumbnails:', regenerated)
