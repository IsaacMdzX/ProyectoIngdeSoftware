from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from urllib.parse import urlparse, urljoin
from ..extensions import db, bcrypt
from .models import Cliente, Admin

auth_bp = Blueprint('auth', __name__, template_folder='templates')


def is_safe_url(target: str) -> bool:
    """Ensure the target URL is relative or same-host to prevent open redirects."""
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('correo')
        contrasena = request.form.get('contrasena')
        
        if not email or not contrasena:
            flash('Por favor, ingrese correo y contraseña.', 'danger')
            return redirect(url_for('auth.login'))

        cliente_existente = db.session.execute(
            db.select(Cliente).filter_by(email=email)
        ).scalar_one_or_none()

        admin_existente = db.session.execute(
            db.select(Admin).filter_by(correo=email)
        ).scalar_one_or_none()

        if admin_existente and bcrypt.check_password_hash(admin_existente.contrasena, contrasena):
            session['user_id'] = admin_existente.id_admin
            session['role'] = 'admin' 
            session['user_name'] = admin_existente.nombre_admin 
            # Reiniciar carrito al iniciar sesión
            session['carrito'] = []
            session.modified = True
            flash(f'Bienvenido, Administrador {admin_existente.nombre_admin}!', 'success')
            next_url = request.args.get('next')
            if next_url and is_safe_url(next_url):
                return redirect(next_url)
            return redirect(url_for('admin.inventario_tenis')) 

        elif cliente_existente and bcrypt.check_password_hash(cliente_existente.contrasena, contrasena):
            session['user_id'] = cliente_existente.id_cliente
            session['role'] = 'cliente'
            session['user_name'] = cliente_existente.nombre_cliente 
            # Reiniciar carrito al iniciar sesión
            session['carrito'] = []
            session.modified = True
            flash(f'¡Bienvenido de vuelta, {cliente_existente.nombre_cliente}!', 'success')
            next_url = request.args.get('next')
            if next_url and is_safe_url(next_url):
                return redirect(next_url)
            return redirect(url_for('public.index')) 
        
        else:
            flash('Correo o contraseña incorrectos.', 'danger')
            return redirect(url_for('auth.login'))

    return render_template('users/login.html') 

@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        next_url = request.args.get('next')
        nombre = request.form.get('nombre')
        email = request.form.get('correo')
        telefono = request.form.get('telefono')
        contrasena = request.form.get('contrasena')
        confirmar_contrasena = request.form.get('confirmar_contrasena')

        if not all([nombre, email, telefono, contrasena, confirmar_contrasena]):
            flash('Todos los campos son obligatorios para el registro.', 'danger')
            return redirect(url_for('auth.registro', next=next_url))

        if contrasena != confirmar_contrasena:
            flash('Las contraseñas no coinciden. Intente de nuevo.', 'danger')
            return redirect(url_for('auth.registro', next=next_url))

        if db.session.execute(db.select(Cliente).filter_by(email=email)).scalar_one_or_none():
            flash('Ya existe una cuenta con este correo. Inicia sesión.', 'warning')
            if next_url and is_safe_url(next_url):
                return redirect(url_for('auth.login', next=next_url))
            return redirect(url_for('auth.login'))

        try:
            hashed_password = bcrypt.generate_password_hash(contrasena).decode('utf-8')
            
            nuevo_cliente = Cliente(
                nombre_cliente=nombre, 
                email=email, 
                telefono=telefono,
                contrasena=hashed_password 
            )
            db.session.add(nuevo_cliente)
            db.session.commit()
            
            flash(f'¡Cuenta creada exitosamente! Por favor, inicia sesión.', 'success')
            if next_url and is_safe_url(next_url):
                return redirect(url_for('auth.login', next=next_url))
            return redirect(url_for('auth.login')) 
            
        except Exception as e:
            db.session.rollback()
        flash('Ocurrió un error inesperado al registrar la cuenta.', 'danger')
        return redirect(url_for('auth.registro', next=next_url))

    return render_template('users/Crear_cuenta.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    session.pop('user_name', None) 
    session.pop('carrito', None)
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('public.index'))