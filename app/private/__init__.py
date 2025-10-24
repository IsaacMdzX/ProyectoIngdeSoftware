from flask import Blueprint, render_template, session, redirect, url_for, flash
from database import db, Cliente, Admin 

private_bp = Blueprint('private', __name__, url_prefix='/private')

@private_bp.route('/gestion-usuarios')
def gestion_usuarios():
    if 'role' not in session or session['role'] != 'admin':
        flash('Acceso denegado. Debes ser un administrador.', 'danger')
        return redirect(url_for('auth.login'))
    
    clientes = db.session.execute(db.select(Cliente)).scalars().all()
    admins = db.session.execute(db.select(Admin)).scalars().all()
    return render_template('private/gestion_clientes.html', clientes=clientes, admins=admins)