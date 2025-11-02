from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from ..extensions import db, bcrypt
from ..auth.models import Cliente, Admin
from ..public.models import Tenis, Playera, Gorra
from .models import Inventario

admin_bp = Blueprint('admin', __name__, template_folder='templates')

@admin_bp.route('/inventario-tenis')
def inventario_tenis():
    if 'role' not in session or session['role'] != 'admin':
        flash('Acceso denegado. Debes ser un administrador.', 'danger')
        return redirect(url_for('auth.login'))
    
    stmt = (
        db.select(Tenis.nombre_tenis, Tenis.precio, Inventario.cantidad, Tenis.id_teni)
        .join(Inventario, (Tenis.id_teni == Inventario.id_producto))
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
        db.select(Playera.nombre_playera, Playera.precio, Inventario.cantidad, Playera.id_playera)
        .join(Inventario, (Playera.id_playera == Inventario.id_producto))
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
        db.select(Gorra.nombre_gorra, Gorra.precio, Inventario.cantidad, Gorra.id_gorra)
        .join(Inventario, (Gorra.id_gorra == Inventario.id_producto))
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