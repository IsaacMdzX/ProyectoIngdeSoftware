from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify
from functools import wraps
from database import db, Admin, Tenis, Playera, Gorra, Marca, Cliente, Inventario

# Crear Blueprint para admin
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Decorador para requerir admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('es_admin'):
            flash('Acceso denegado. Se requieren privilegios de administrador.', 'error')
            return redirect(url_for('admin.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== RUTAS DE AUTENTICACIÓN ====================

# Ruta de login admin (GET)
@admin_bp.route('/login', methods=['GET'])
def admin_login():
    if session.get('es_admin'):
        return redirect(url_for('admin.admin_dashboard'))
    return render_template('private/login.html')

# Procesar login admin (POST)
@admin_bp.route('/login', methods=['POST'])
def admin_login_post():
    try:
        username = request.form['username']
        password = request.form['password']
        
        # Buscar administrador usando tu modelo Admin de database.py
        admin = Admin.query.filter(
            (Admin.correo == username) | (Admin.nombre_admin == username)
        ).first()
        
        if admin and admin.contrasena == password:
            session['user_id'] = admin.id_admin
            session['es_admin'] = True
            session['username'] = admin.nombre_admin
            session['email'] = admin.correo
            
            flash('¡Bienvenido al panel de administración!', 'success')
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Credenciales de administrador incorrectas', 'error')
            return redirect(url_for('admin.admin_login'))
            
    except Exception as e:
        flash(f'Error en el login: {str(e)}', 'error')
        return redirect(url_for('admin.admin_login'))

# Cerrar sesión admin
@admin_bp.route('/logout')
def admin_logout():
    session.pop('user_id', None)
    session.pop('es_admin', None)
    session.pop('username', None)
    session.pop('email', None)
    flash('Sesión de administrador cerrada', 'info')
    return redirect(url_for('admin.admin_login'))

# ==================== RUTAS PRINCIPALES ====================

# Dashboard principal admin
@admin_bp.route('/dashboard')
@admin_required
def admin_dashboard():
    try:
        tenis = Tenis.query.all()
        total_tenis = Tenis.query.count()
        total_marcas = Marca.query.count()
        
        stats = {
            'total_tenis': total_tenis,
            'total_marcas': total_marcas,
            'total_stock': 0
        }
        
        return render_template('private/Inventario_tenis.html',
                             productos=tenis, 
                             stats=stats,
                             username=session.get('username'))
        
    except Exception as e:
        flash(f'Error al cargar el dashboard: {str(e)}', 'error')
        return render_template('private/Inventario_tenis.html',
                             productos=[], 
                             stats={},
                             username=session.get('username'))

# Gestión de playeras - QUITA @admin_required temporalmente
@admin_bp.route('/playeras')
# @admin_required  # 👈 COMENTA ESTA LÍNEA TEMPORALMENTE
def gestion_playeras():
    try:
        print("🔍 ACCEDIENDO A RUTA PLAYERAS")
        playeras = Playera.query.all()
        print(f"📊 Playeras encontradas: {len(playeras)}")
        
        return render_template('private/Inventario_playeras.html',
                             productos=playeras, 
                             username=session.get('username'))
        
    except Exception as e:
        print(f"❌ ERROR en playeras: {e}")
        flash(f'Error al cargar playeras: {str(e)}', 'error')
        return render_template('private/Inventario_playeras.html',
                             productos=[], 
                             username=session.get('username'))

# Gestión de gorras - QUITA @admin_required temporalmente  
@admin_bp.route('/gorras')
# @admin_required  # 👈 COMENTA ESTA LÍNEA TEMPORALMENTE
def gestion_gorras():
    try:
        print("🔍 ACCEDIENDO A RUTA GORRAS")
        gorras = Gorra.query.all()
        print(f"📊 Gorras encontradas: {len(gorras)}")
        
        return render_template('private/Inventario_gorras.html',
                             productos=gorras, 
                             username=session.get('username'))
        
    except Exception as e:
        print(f"❌ ERROR en gorras: {e}")
        flash(f'Error al cargar gorras: {str(e)}', 'error')
        return render_template('private/Inventario_gorras.html',
                             productos=[], 
                             username=session.get('username'))

# Ruta por defecto para admin
@admin_bp.route('/')
def admin_index():
    if session.get('es_admin'):
        return redirect(url_for('admin.admin_dashboard'))
    return redirect(url_for('admin.admin_login'))