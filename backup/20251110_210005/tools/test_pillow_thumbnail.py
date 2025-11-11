from PIL import Image, ImageDraw
import os, uuid

BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
IMG_DIR = os.path.join(BASE_DIR, 'app', 'static', 'images', 'product_images')
SMALL_DIR = os.path.join(IMG_DIR, 'thumbs', 'small')
MED_DIR = os.path.join(IMG_DIR, 'thumbs', 'medium')

os.makedirs(SMALL_DIR, exist_ok=True)
os.makedirs(MED_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)

# Create a test image
img = Image.new('RGB', (1200, 800), (200, 30, 30))
d = ImageDraw.Draw(img)
d.text((10, 10), 'Pillow test image', fill=(255, 255, 255))

fname = f"{uuid.uuid4().hex}.jpg"
orig_path = os.path.join(IMG_DIR, fname)
img.save(orig_path, quality=85)

# Medium: max width 800, keep aspect ratio
w, h = img.size
if w > 800:
    new_h = int(h * (800.0 / w))
    medium = img.resize((800, new_h), Image.LANCZOS)
else:
    medium = img.copy()

medium_path = os.path.join(MED_DIR, fname)
medium.save(medium_path, quality=85)

# Small: thumbnail up to 150x150 (keeps aspect ratio)
small = img.copy()
small.thumbnail((150, 150), Image.LANCZOS)
small_path = os.path.join(SMALL_DIR, fname)
small.save(small_path, quality=85)

print('CREATED:')
print(' original:', orig_path)
print(' medium :', medium_path)
print(' small  :', small_path)
