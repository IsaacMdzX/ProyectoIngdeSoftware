from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from ..extensions import db, bcrypt
from ..auth.models import Cliente, Admin
from ..public.models import Tenis, Playera, Gorra, Marca, TipoProducto, TallaCalzado, TallaRopa, Color, Genero
from .models import Inventario, Pedido, DetallePedido, Entrega, Transferencia

admin_bp = Blueprint('admin', __name__, template_folder='templates')

def to_none(val):
    return None if val == '' else val

@admin_bp.route('/inventario-tenis')
def inventario_tenis():
    if 'role' not in session or session['role'] != 'admin':
        flash('Acceso denegado. Debes ser un administrador.', 'danger')
        return redirect(url_for('auth.login'))
    
    stmt = (
        db.select(Tenis, Inventario.cantidad)
        .join(Inventario, (Tenis.id_teni == Inventario.id_producto), isouter=True)
        .filter(Inventario.tipo_producto == 'Tenis')
    )
    productos_inventario = db.session.execute(stmt).all()

    return render_template('admin/Inventario_tenis.html', inventario=productos_inventario)

@admin_bp.route('/inventario-playeras')
def inventario_playeras():
    if 'role' not in session or session['role'] != 'admin':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('auth.login'))
    
    stmt = (
        db.select(Playera, Inventario.cantidad)
        .join(Inventario, (Playera.id_playera == Inventario.id_producto), isouter=True)
        .filter(Inventario.tipo_producto == 'Playera')
    )
    productos_inventario = db.session.execute(stmt).all()

    return render_template('admin/Inventario_playeras.html', inventario=productos_inventario)

@admin_bp.route('/inventario-gorras')
def inventario_gorras():
    if 'role' not in session or session['role'] != 'admin':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('auth.login'))
    
    stmt = (
        db.select(Gorra, Inventario.cantidad)
        .join(Inventario, (Gorra.id_gorra == Inventario.id_producto), isouter=True)
        .filter(Inventario.tipo_producto == 'Gorra')
    )
    productos_inventario = db.session.execute(stmt).all()

    return render_template('admin/Inventario_gorras.html', inventario=productos_inventario)

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
                    descripcion=to_none(request.form.get('descripcion'))
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
                    descripcion=to_none(request.form.get('descripcion'))
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
                    descripcion=to_none(request.form.get('descripcion'))
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
            return redirect(url_for('admin.inventario_tenis'))

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