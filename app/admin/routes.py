from flask import Blueprint, render_template, session, redirect, url_for, flash, request, current_app
import os
from werkzeug.utils import secure_filename
from uuid import uuid4
from flask import url_for

# Image processing (optional)
try:
    from PIL import Image, ImageOps
    HAS_PIL = True
except Exception:
    HAS_PIL = False

# Upload configuration
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif'}
# 2 MB
MAX_UPLOAD_SIZE = 2 * 1024 * 1024
from ..extensions import db, bcrypt
from ..auth.models import Cliente, Admin
from ..public.models import Tenis, Playera, Gorra, Marca, TipoProducto, TallaCalzado, TallaRopa, Color, Genero
from .models import Inventario, Pedido, DetallePedido, Entrega, Transferencia

admin_bp = Blueprint('admin', __name__, template_folder='templates')


def _resolve_image_url_admin(filename: str):
    """Return best static URL for a product image: small thumb -> original -> placeholder."""
    try:
        if not filename:
            return url_for('static', filename='images/placeholder.svg')
        thumb_rel = os.path.join('images', 'product_images', 'thumbs', 'small', filename)
        orig_rel = os.path.join('images', 'product_images', filename)
        thumb_path = os.path.join(current_app.static_folder, thumb_rel)
        orig_path = os.path.join(current_app.static_folder, orig_rel)
        if os.path.exists(thumb_path):
            return url_for('static', filename=thumb_rel)
        if os.path.exists(orig_path):
            return url_for('static', filename=orig_rel)
    except Exception:
        current_app.logger.debug('Error resolviendo image_url admin para %s', filename)
    return url_for('static', filename='images/placeholder.svg')


def _create_square_thumbs(orig_path: str, small_path: str, medium_path: str):
    """Create center-cropped square thumbnails for small and medium sizes.

    Overwrites target files if they exist. Uses Pillow and preserves reasonable
    JPEG quality. Raises exceptions if processing fails.
    """
    if not HAS_PIL:
        raise RuntimeError('Pillow not available')

    from PIL import Image

    with Image.open(orig_path) as im:
        # ensure consistent orientation (respect EXIF)
        try:
            im = ImageOps.exif_transpose(im)
        except Exception:
            # fallback if ImageOps not available or fails
            pass

        # create square crop based on shortest edge
        width, height = im.size
        side = min(width, height)
        left = (width - side) // 2
        top = (height - side) // 2
        right = left + side
        bottom = top + side
        square = im.crop((left, top, right, bottom))

        # small thumb (square)
        small = square.copy()
        small = small.resize((400, 400), Image.LANCZOS)
        small.save(small_path, quality=85)

        # medium thumb (square)
        medium = square.copy()
        medium = medium.resize((800, 800), Image.LANCZOS)
        medium.save(medium_path, quality=90)

# Requiere sesión de administrador para cualquier ruta del blueprint
@admin_bp.before_request
def require_admin_session():
    if session.get('role') != 'admin':
        flash('Acceso denegado. Debes iniciar sesión como administrador.', 'danger')
        return redirect(url_for('auth.login'))

def to_none(val):
    return None if val == '' else val

@admin_bp.route('/inventario-tenis')
def inventario_tenis():
    if 'role' not in session or session['role'] != 'admin':
        flash('Acceso denegado. Debes ser un administrador.', 'danger')
        return redirect(url_for('auth.login'))

    # Parámetros de búsqueda y paginación
    q = (request.args.get('q') or '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)

    # Base count por nombre
    count_stmt = db.select(db.func.count()).select_from(Tenis)
    if q:
        count_stmt = count_stmt.where(Tenis.nombre_tenis.ilike(f"%{q}%"))
    total = db.session.execute(count_stmt).scalar()

    # Mostrar todos los tenis, con cantidad del inventario si existe (0 si no)
    stmt = (
        db.select(Tenis, Inventario.cantidad)
        .join(
            Inventario,
            db.and_(Tenis.id_teni == Inventario.id_producto, Inventario.tipo_producto == 'Tenis'),
            isouter=True,
        )
    )
    if q:
        stmt = stmt.where(Tenis.nombre_tenis.ilike(f"%{q}%"))
    stmt = stmt.offset((page - 1) * per_page).limit(per_page)

    productos_inventario = db.session.execute(stmt).all()

    # attach image_url for templates
    for prod, cantidad in productos_inventario:
        try:
            fn = getattr(prod, 'image_filename', None)
            setattr(prod, 'image_url', _resolve_image_url_admin(fn))
        except Exception:
            setattr(prod, 'image_url', url_for('static', filename='images/placeholder.svg'))

    return render_template('admin/Inventario_tenis.html', inventario=productos_inventario, q=q, page=page, per_page=per_page, total=total)

@admin_bp.route('/inventario-playeras')
def inventario_playeras():
    if 'role' not in session or session['role'] != 'admin':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('auth.login'))

    q = (request.args.get('q') or '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)

    count_stmt = db.select(db.func.count()).select_from(Playera)
    if q:
        count_stmt = count_stmt.where(Playera.nombre_playera.ilike(f"%{q}%"))
    total = db.session.execute(count_stmt).scalar()

    stmt = (
        db.select(Playera, Inventario.cantidad)
        .join(
            Inventario,
            db.and_(Playera.id_playera == Inventario.id_producto, Inventario.tipo_producto == 'Playera'),
            isouter=True,
        )
    )
    if q:
        stmt = stmt.where(Playera.nombre_playera.ilike(f"%{q}%"))
    stmt = stmt.offset((page - 1) * per_page).limit(per_page)

    productos_inventario = db.session.execute(stmt).all()

    for prod, cantidad in productos_inventario:
        try:
            fn = getattr(prod, 'image_filename', None)
            setattr(prod, 'image_url', _resolve_image_url_admin(fn))
        except Exception:
            setattr(prod, 'image_url', url_for('static', filename='images/placeholder.svg'))

    return render_template('admin/Inventario_playeras.html', inventario=productos_inventario, q=q, page=page, per_page=per_page, total=total)

@admin_bp.route('/inventario-gorras')
def inventario_gorras():
    if 'role' not in session or session['role'] != 'admin':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('auth.login'))

    q = (request.args.get('q') or '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)

    count_stmt = db.select(db.func.count()).select_from(Gorra)
    if q:
        count_stmt = count_stmt.where(Gorra.nombre_gorra.ilike(f"%{q}%"))
    total = db.session.execute(count_stmt).scalar()

    stmt = (
        db.select(Gorra, Inventario.cantidad)
        .join(
            Inventario,
            db.and_(Gorra.id_gorra == Inventario.id_producto, Inventario.tipo_producto == 'Gorra'),
            isouter=True,
        )
    )
    if q:
        stmt = stmt.where(Gorra.nombre_gorra.ilike(f"%{q}%"))
    stmt = stmt.offset((page - 1) * per_page).limit(per_page)

    productos_inventario = db.session.execute(stmt).all()

    for prod, cantidad in productos_inventario:
        try:
            fn = getattr(prod, 'image_filename', None)
            setattr(prod, 'image_url', _resolve_image_url_admin(fn))
        except Exception:
            setattr(prod, 'image_url', url_for('static', filename='images/placeholder.svg'))

    return render_template('admin/Inventario_gorras.html', inventario=productos_inventario, q=q, page=page, per_page=per_page, total=total)

@admin_bp.route('/gestion-usuarios')
def gestion_usuarios():
    if 'role' not in session or session['role'] != 'admin':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('auth.login'))

    clientes = db.session.execute(db.select(Cliente)).scalars().all()
    admins = db.session.execute(db.select(Admin)).scalars().all()
    
    return render_template('admin/gestion_clientes.html', clientes=clientes, admins=admins)

@admin_bp.route('/agregar-usuario', methods=['GET', 'POST'])
def agregar_usuario():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('correo')
        telefono = request.form.get('telefono')
        contrasena = request.form.get('contrasena')
        rol = request.form.get('rol')
        
        if not all([nombre, email, telefono, contrasena, rol]):
            flash('Todos los campos son obligatorios.', 'danger')
            return redirect(url_for('admin.agregar_usuario'))
        
        hashed_password = bcrypt.generate_password_hash(contrasena).decode('utf-8')
        
        try:
            if rol == 'cliente':
                nuevo_usuario = Cliente(
                    nombre_cliente=nombre, 
                    email=email, 
                    telefono=telefono, 
                    contrasena=hashed_password
                )
            elif rol == 'admin':
                nuevo_usuario = Admin(
                    nombre_admin=nombre, 
                    correo=email, 
                    telefono=telefono, 
                    contrasena=hashed_password
                )
            else:
                flash('Rol no válido.', 'danger')
                return redirect(url_for('admin.agregar_usuario'))
            
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash('Usuario agregado exitosamente.', 'success')
            return redirect(url_for('admin.gestion_usuarios'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar usuario: {e}', 'danger')
            return redirect(url_for('admin.agregar_usuario'))

    return render_template('admin/agregar_usuario.html')

@admin_bp.route('/editar-usuario/<string:rol>/<int:id>', methods=['GET', 'POST'])
def editar_usuario(rol, id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))

    if rol == 'cliente':
        usuario = db.session.get(Cliente, id)
    elif rol == 'admin':
        usuario = db.session.get(Admin, id)
    else:
        flash('Rol no válido.', 'danger')
        return redirect(url_for('admin.gestion_usuarios'))

    if not usuario:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('admin.gestion_usuarios'))

    if request.method == 'POST':
        try:
            if rol == 'cliente':
                usuario.nombre_cliente = request.form.get('nombre')
                usuario.email = request.form.get('correo')
                usuario.telefono = request.form.get('telefono')
            elif rol == 'admin':
                usuario.nombre_admin = request.form.get('nombre')
                usuario.correo = request.form.get('correo')
                usuario.telefono = request.form.get('telefono')

            db.session.commit()
            flash('Usuario actualizado exitosamente.', 'success')
            return redirect(url_for('admin.gestion_usuarios'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar usuario: {e}', 'danger')
            return redirect(url_for('admin.editar_usuario', rol=rol, id=id))

    return render_template('admin/editar_usuario.html', usuario=usuario, rol=rol)


@admin_bp.route('/eliminar-usuario/<string:rol>/<int:id>', methods=['POST'])
def eliminar_usuario(rol, id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))
    
    try:
        if rol == 'cliente':
            usuario = db.session.get(Cliente, id)
        elif rol == 'admin':
            usuario = db.session.get(Admin, id)
        else:
            flash('Rol no válido.', 'danger')
            return redirect(url_for('admin.gestion_usuarios'))

        if usuario:
            db.session.delete(usuario)
            db.session.commit()
            flash('Usuario eliminado exitosamente.', 'success')
        else:
            flash('Usuario no encontrado.', 'warning')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar usuario: {e}', 'danger')

    return redirect(url_for('admin.gestion_usuarios'))

@admin_bp.route('/cambiar-contrasena', methods=['GET', 'POST'])
def cambiar_contrasena():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        contrasena_actual = request.form.get('contrasena_actual')
        nueva_contrasena = request.form.get('nueva_contrasena')
        confirmar_contrasena = request.form.get('confirmar_contrasena')

        if not all([contrasena_actual, nueva_contrasena, confirmar_contrasena]):
            flash('Todos los campos son obligatorios.', 'danger')
            return redirect(url_for('admin.cambiar_contrasena'))
        
        if nueva_contrasena != confirmar_contrasena:
            flash('Las nuevas contraseñas no coinciden.', 'danger')
            return redirect(url_for('admin.cambiar_contrasena'))

        admin_id = session.get('user_id')
        admin = db.session.get(Admin, admin_id)

        if not bcrypt.check_password_hash(admin.contrasena, contrasena_actual):
            flash('La contraseña actual es incorrecta.', 'danger')
            return redirect(url_for('admin.cambiar_contrasena'))
        
        try:
            hashed_password = bcrypt.generate_password_hash(nueva_contrasena).decode('utf-8')
            admin.contrasena = hashed_password
            db.session.commit()
            flash('Contraseña actualizada exitosamente.', 'success')
            return redirect(url_for('admin.inventario_tenis'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la contraseña: {e}', 'danger')
            return redirect(url_for('admin.cambiar_contrasena'))

    return render_template('admin/cambiar_contrasena.html')

@admin_bp.route('/agregar-producto', methods=['GET', 'POST'])
def agregar_producto():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        categoria = request.form.get('categoria')
        
        # Handle optional image upload (validate extension and size)
        imagen_file = request.files.get('imagen') if 'imagen' in request.files else None
        saved_image_filename = None
        try:
            if imagen_file and imagen_file.filename:
                upload_dir = os.path.join(current_app.static_folder, 'images', 'product_images')
                os.makedirs(upload_dir, exist_ok=True)
                filename = secure_filename(imagen_file.filename)
                name, ext = os.path.splitext(filename)
                ext = ext.lower()
                if ext not in ALLOWED_EXTENSIONS:
                    flash('Tipo de archivo no permitido. Usa png, jpg, jpeg o gif.', 'danger')
                    return redirect(url_for('admin.agregar_producto'))
                # Read into memory up to limit to enforce size
                imagen_file.stream.seek(0, os.SEEK_END)
                filesize = imagen_file.stream.tell()
                imagen_file.stream.seek(0)
                if filesize > MAX_UPLOAD_SIZE:
                    flash('El archivo es demasiado grande (máx 2MB).', 'danger')
                    return redirect(url_for('admin.agregar_producto'))
                # Prepend uuid to avoid collisions
                filename = f"{uuid4().hex}{ext}"
                imagen_path = os.path.join(upload_dir, filename)
                # Try to save file and create thumbnails; if any step fails, clean up and do not set image name
                try:
                    imagen_file.save(imagen_path)
                    if not os.path.exists(imagen_path) or os.path.getsize(imagen_path) == 0:
                        raise IOError('Saved file missing or empty')
                    # Extra safety: check saved file size
                    if os.path.getsize(imagen_path) > MAX_UPLOAD_SIZE:
                        os.remove(imagen_path)
                        flash('El archivo es demasiado grande (máx 2MB).', 'danger')
                        return redirect(url_for('admin.agregar_producto'))

                    # create thumbnails if Pillow is available (small + medium)
                    if HAS_PIL:
                        small_dir = os.path.join(upload_dir, 'thumbs', 'small')
                        medium_dir = os.path.join(upload_dir, 'thumbs', 'medium')
                        os.makedirs(small_dir, exist_ok=True)
                        os.makedirs(medium_dir, exist_ok=True)
                        small_path = os.path.join(small_dir, filename)
                        medium_path = os.path.join(medium_dir, filename)
                        try:
                            _create_square_thumbs(imagen_path, small_path, medium_path)
                        except Exception:
                            # if thumbnail creation fails, remove partial files and raise
                            if os.path.exists(imagen_path):
                                try:
                                    os.remove(imagen_path)
                                except Exception:
                                    pass
                            if os.path.exists(small_path):
                                try:
                                    os.remove(small_path)
                                except Exception:
                                    pass
                            if os.path.exists(medium_path):
                                try:
                                    os.remove(medium_path)
                                except Exception:
                                    pass
                            raise

                    # If we reached here, file saved successfully
                    saved_image_filename = filename
                except Exception as e:
                    current_app.logger.exception('Error guardando la imagen del producto: %s', e)
                    flash('Error al procesar la imagen. Intenta de nuevo.', 'danger')
                    # ensure no leftover file
                    try:
                        if os.path.exists(imagen_path):
                            os.remove(imagen_path)
                    except Exception:
                        pass

        except Exception as e:
            current_app.logger.exception('Error procesando la imagen en agregar_producto: %s', e)

        try:
            if categoria == 'tenis':
                nombre = request.form.get('nombre')
                marca = request.form.get('marca')
                tipo = request.form.get('tipo')
                precio = request.form.get('precio')
                
                if not all([nombre, marca, tipo, precio]):
                    flash('Error: Nombre, Marca, Tipo y Precio son obligatorios para Tenis.', 'danger')
                    return redirect(url_for('admin.agregar_producto'))

                nuevo_producto = Tenis(
                    nombre_tenis=nombre,
                    marca=marca,
                    tipo=tipo,
                    talla_calzado=to_none(request.form.get('talla_calzado')),
                    precio=precio,
                    descripcion=to_none(request.form.get('descripcion')),
                    image_filename=saved_image_filename
                )
                id_producto_attr = 'id_teni'
                
            elif categoria == 'playera':
                nombre = request.form.get('nombre')
                marca = request.form.get('marca')
                precio = request.form.get('precio')

                if not all([nombre, marca, precio]):
                    flash('Error: Nombre, Marca y Precio son obligatorios para Playeras.', 'danger')
                    return redirect(url_for('admin.agregar_producto'))
                
                nuevo_producto = Playera(
                    nombre_playera=nombre,
                    marca=marca,
                    tipo=to_none(request.form.get('tipo')),
                    talla_ropa=to_none(request.form.get('talla_ropa')),
                    genero=to_none(request.form.get('genero')),
                    material=to_none(request.form.get('material')),
                    precio=precio,
                    descripcion=to_none(request.form.get('descripcion')),
                    image_filename=saved_image_filename
                )
                id_producto_attr = 'id_playera'

            elif categoria == 'gorra':
                nombre = request.form.get('nombre')
                precio = request.form.get('precio')

                if not all([nombre, precio]):
                    flash('Error: Nombre y Precio son obligatorios para Gorras.', 'danger')
                    return redirect(url_for('admin.agregar_producto'))

                nuevo_producto = Gorra(
                    nombre_gorra=nombre,
                    talla_ropa=to_none(request.form.get('talla_ropa')),
                    precio=precio,
                    descripcion=to_none(request.form.get('descripcion')),
                    image_filename=saved_image_filename
                )
                id_producto_attr = 'id_gorra'
            
            else:
                flash('Categoría no válida.', 'danger')
                return redirect(url_for('admin.agregar_producto'))

        except Exception as e:
            flash(f'Error al preparar el producto: {e}', 'danger')
            return redirect(url_for('admin.agregar_producto'))

        try:
            db.session.add(nuevo_producto)
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar el producto (PASO 2): {e}', 'danger')
            return redirect(url_for('admin.agregar_producto'))

        try:
            id_prod_guardado = getattr(nuevo_producto, id_producto_attr)
            
            nuevo_inventario = Inventario(
                tipo_producto=categoria.capitalize(),
                id_producto=id_prod_guardado,
                cantidad=request.form.get('cantidad', 0)
            )
            db.session.add(nuevo_inventario)
            db.session.commit()
            
            flash(f'Producto ({categoria}) agregado exitosamente.', 'success')
            # Redirigir al inventario correspondiente según la categoría
            if categoria == 'tenis':
                return redirect(url_for('admin.inventario_tenis'))
            elif categoria == 'playera':
                return redirect(url_for('admin.inventario_playeras'))
            else:
                return redirect(url_for('admin.inventario_gorras'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar el inventario (PASO 3): {e}', 'danger')
            return redirect(url_for('admin.agregar_producto'))

    marcas = db.session.execute(db.select(Marca)).scalars().all()
    tipos = db.session.execute(db.select(TipoProducto)).scalars().all()
    tallas_calzado = db.session.execute(db.select(TallaCalzado)).scalars().all()
    tallas_ropa = db.session.execute(db.select(TallaRopa)).scalars().all()
    generos = db.session.execute(db.select(Genero)).scalars().all()
    
    return render_template('admin/nuevo_producto.html', 
                           marcas=marcas, 
                           tipos=tipos, 
                           tallas_calzado=tallas_calzado,
                           tallas_ropa=tallas_ropa,
                           generos=generos)

@admin_bp.route('/editar-producto/<string:tipo>/<int:id>', methods=['GET', 'POST'])
def editar_producto(tipo, id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))

    if tipo == 'Tenis':
        producto = db.session.get(Tenis, id)
        redirect_url = url_for('admin.inventario_tenis')
    elif tipo == 'Playera':
        producto = db.session.get(Playera, id)
        redirect_url = url_for('admin.inventario_playeras')
    elif tipo == 'Gorra':
        producto = db.session.get(Gorra, id)
        redirect_url = url_for('admin.inventario_gorras')
    else:
        flash('Tipo de producto no válido.', 'danger')
        return redirect(url_for('admin.inventario_tenis'))

    inventario = db.session.execute(
        db.select(Inventario).filter_by(tipo_producto=tipo, id_producto=id)
    ).scalar_one_or_none()
    
    if not producto:
        flash('Producto no encontrado.', 'danger')
        return redirect(url_for('admin.inventario_tenis'))

    if request.method == 'POST':
        try:
            if tipo == 'Tenis':
                producto.nombre_tenis = request.form.get('nombre')
                producto.marca = request.form.get('marca')
                producto.tipo = request.form.get('tipo')
                producto.talla_calzado = to_none(request.form.get('talla_calzado'))
                producto.precio = request.form.get('precio')
                producto.descripcion = to_none(request.form.get('descripcion'))
            elif tipo == 'Playera':
                producto.nombre_playera = request.form.get('nombre')
                producto.marca = request.form.get('marca')
                producto.tipo = to_none(request.form.get('tipo'))
                producto.talla_ropa = to_none(request.form.get('talla_ropa'))
                producto.genero = to_none(request.form.get('genero'))
                producto.material = to_none(request.form.get('material'))
                producto.precio = request.form.get('precio')
                producto.descripcion = to_none(request.form.get('descripcion'))
            elif tipo == 'Gorra':
                producto.nombre_gorra = request.form.get('nombre')
                producto.talla_ropa = to_none(request.form.get('talla_ropa'))
                producto.precio = request.form.get('precio')
                producto.descripcion = to_none(request.form.get('descripcion'))

            # Procesar posible nueva imagen en la edición
            try:
                imagen_file = request.files.get('imagen') if 'imagen' in request.files else None
                if imagen_file and imagen_file.filename:
                    # validar extensión
                    filename = secure_filename(imagen_file.filename)
                    name, ext = os.path.splitext(filename)
                    ext = ext.lower()
                    if ext not in ALLOWED_EXTENSIONS:
                        flash('Tipo de archivo no permitido. Usa png, jpg, jpeg o gif.', 'danger')
                        return redirect(url_for('admin.editar_producto', tipo=tipo, id=id))
                    # validar tamaño
                    imagen_file.stream.seek(0, os.SEEK_END)
                    filesize = imagen_file.stream.tell()
                    imagen_file.stream.seek(0)
                    if filesize > MAX_UPLOAD_SIZE:
                        flash('El archivo es demasiado grande (máx 2MB).', 'danger')
                        return redirect(url_for('admin.editar_producto', tipo=tipo, id=id))
                    # guardar nueva imagen
                    upload_dir = os.path.join(current_app.static_folder, 'images', 'product_images')
                    os.makedirs(upload_dir, exist_ok=True)
                    new_filename = f"{uuid4().hex}{ext}"
                    imagen_path = os.path.join(upload_dir, new_filename)
                    imagen_file.save(imagen_path)
                    # crear miniaturas para la nueva imagen si Pillow está disponible
                    try:
                        if HAS_PIL:
                            small_dir = os.path.join(upload_dir, 'thumbs', 'small')
                            medium_dir = os.path.join(upload_dir, 'thumbs', 'medium')
                            os.makedirs(small_dir, exist_ok=True)
                            os.makedirs(medium_dir, exist_ok=True)
                            small_path = os.path.join(small_dir, new_filename)
                            medium_path = os.path.join(medium_dir, new_filename)
                            try:
                                _create_square_thumbs(imagen_path, small_path, medium_path)
                            except Exception:
                                # si falla la creación de miniaturas, borrar archivos nuevos y mostrar log
                                if os.path.exists(imagen_path):
                                    try:
                                        os.remove(imagen_path)
                                    except Exception:
                                        pass
                                if os.path.exists(small_path):
                                    try:
                                        os.remove(small_path)
                                    except Exception:
                                        pass
                                if os.path.exists(medium_path):
                                    try:
                                        os.remove(medium_path)
                                    except Exception:
                                        pass
                                raise
                    except Exception:
                        current_app.logger.exception('Error creando miniaturas en edición')
                    # eliminar imagen anterior si existe
                    old_filename = getattr(producto, 'image_filename', None)
                    if old_filename:
                        try:
                            old_path = os.path.join(upload_dir, old_filename)
                            if os.path.exists(old_path):
                                os.remove(old_path)
                            # remove old small/medium thumbs if present
                            old_small = os.path.join(upload_dir, 'thumbs', 'small', old_filename)
                            old_medium = os.path.join(upload_dir, 'thumbs', 'medium', old_filename)
                            if os.path.exists(old_small):
                                os.remove(old_small)
                            if os.path.exists(old_medium):
                                os.remove(old_medium)
                        except Exception:
                            current_app.logger.exception('Error borrando imagen antigua: %s', old_filename)
                    producto.image_filename = new_filename
            except Exception:
                current_app.logger.exception('Error procesando la imagen en edición')
            
            if inventario:
                inventario.cantidad = request.form.get('cantidad', 0)
            else:
                nuevo_inventario = Inventario(
                    tipo_producto=tipo,
                    id_producto=id,
                    cantidad=request.form.get('cantidad', 0)
                )
                db.session.add(nuevo_inventario)
                
            db.session.commit()
            flash('Producto actualizado exitosamente.', 'success')
            return redirect(redirect_url)
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar producto: {e}', 'danger')
            return redirect(url_for('admin.editar_producto', tipo=tipo, id=id))

    marcas = db.session.execute(db.select(Marca)).scalars().all()
    tipos = db.session.execute(db.select(TipoProducto)).scalars().all()
    tallas_calzado = db.session.execute(db.select(TallaCalzado)).scalars().all()
    tallas_ropa = db.session.execute(db.select(TallaRopa)).scalars().all()
    generos = db.session.execute(db.select(Genero)).scalars().all()

    return render_template('admin/editar_producto.html', 
                           producto=producto, 
                           inventario=inventario,
                           tipo_producto=tipo,
                           marcas=marcas, 
                           tipos=tipos, 
                           tallas_calzado=tallas_calzado,
                           tallas_ropa=tallas_ropa,
                           generos=generos)


@admin_bp.route('/eliminar-producto/<string:tipo>/<int:id>', methods=['POST'])
def eliminar_producto(tipo, id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))
    
    redirect_url = url_for('admin.inventario_tenis')
    
    try:
        inventario_entry = db.session.execute(
            db.select(Inventario).filter_by(tipo_producto=tipo, id_producto=id)
        ).scalar_one_or_none()
        
        if tipo == 'Tenis':
            producto_entry = db.session.get(Tenis, id)
            redirect_url = url_for('admin.inventario_tenis')
        elif tipo == 'Playera':
            producto_entry = db.session.get(Playera, id)
            redirect_url = url_for('admin.inventario_playeras')
        elif tipo == 'Gorra':
            producto_entry = db.session.get(Gorra, id)
            redirect_url = url_for('admin.inventario_gorras')
        else:
            flash('Tipo de producto no válido.', 'danger')
            return redirect(url_for('admin.inventario_tenis'))

        if inventario_entry:
            db.session.delete(inventario_entry)
        if producto_entry:
            # antes de borrar, eliminar imagen asociada si existe
            try:
                imgname = getattr(producto_entry, 'image_filename', None)
                if imgname:
                    img_path = os.path.join(current_app.static_folder, 'images', 'product_images', imgname)
                    small_thumb = os.path.join(current_app.static_folder, 'images', 'product_images', 'thumbs', 'small', imgname)
                    medium_thumb = os.path.join(current_app.static_folder, 'images', 'product_images', 'thumbs', 'medium', imgname)
                    if os.path.exists(img_path):
                        os.remove(img_path)
                    if os.path.exists(small_thumb):
                        os.remove(small_thumb)
                    if os.path.exists(medium_thumb):
                        os.remove(medium_thumb)
            except Exception:
                current_app.logger.exception('Error borrando imagen al eliminar producto')
            db.session.delete(producto_entry)
        
        if inventario_entry or producto_entry:
            db.session.commit()
            flash(f'{tipo} eliminado exitosamente.', 'success')
        else:
            flash('Producto no encontrado.', 'warning')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar {tipo}: {e}', 'danger')

    return redirect(redirect_url)


@admin_bp.route('/regenerate-thumbs', methods=['POST', 'GET'])
def regenerate_thumbs():
    """Regenerate missing small/medium thumbnails for all products.

    Accessible only to admins. Scans Tenis, Playera, Gorra tables and for each
    product with an image_filename will recreate missing thumbnails from the
    original image when Pillow is available.
    """
    if 'role' not in session or session['role'] != 'admin':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('auth.login'))

    upload_dir = os.path.join(current_app.static_folder, 'images', 'product_images')
    small_dir = os.path.join(upload_dir, 'thumbs', 'small')
    medium_dir = os.path.join(upload_dir, 'thumbs', 'medium')
    os.makedirs(small_dir, exist_ok=True)
    os.makedirs(medium_dir, exist_ok=True)

    processed = 0
    created_map = []

    if not HAS_PIL:
        flash('Pillow no está disponible en el entorno; no se pueden crear miniaturas.', 'warning')
        return redirect(url_for('admin.inventario_tenis'))

    try:
        models = [(Tenis, 'Tenis'), (Playera, 'Playera'), (Gorra, 'Gorra')]
        for model, label in models:
            rows = db.session.execute(db.select(model)).scalars().all()
            for prod in rows:
                fn = getattr(prod, 'image_filename', None)
                if not fn:
                    continue
                orig_path = os.path.join(upload_dir, fn)
                small_path = os.path.join(small_dir, fn)
                medium_path = os.path.join(medium_dir, fn)
                created = []
                if not os.path.exists(orig_path):
                    current_app.logger.warning('Original faltante para %s: %s', label, fn)
                    continue
                try:
                    created_local = []
                    # create thumbnails if missing using helper
                    if not os.path.exists(small_path) or not os.path.exists(medium_path):
                        _create_square_thumbs(orig_path, small_path, medium_path)
                        if not os.path.exists(small_path):
                            # if helper didn't create small, mark as missing
                            pass
                        else:
                            created_local.append('small')
                        if not os.path.exists(medium_path):
                            pass
                        else:
                            created_local.append('medium')
                        created.extend(created_local)
                except Exception:
                    current_app.logger.exception('Error creando miniaturas para %s', fn)
                if created:
                    processed += 1
                    created_map.append((label, getattr(prod, getattr(prod, 'id_teni', 'id') if hasattr(prod, 'id_teni') else 'id'), fn, ','.join(created)))
    except Exception:
        current_app.logger.exception('Error durante la regeneración de miniaturas')

    flash(f'Regeneración completada. Productos procesados: {processed}', 'success')
    return redirect(url_for('admin.inventario_tenis'))