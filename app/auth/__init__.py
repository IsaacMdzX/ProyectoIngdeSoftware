from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy.exc import IntegrityError
from database import db, Cliente 


auth_bp = Blueprint('auth', __name__, url_prefix='/auth') 


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('correo')
        telefono = request.form.get('telefono')


        print("Datos recibidos desde el formulario")
        print(f"Nombre: {nombre}")
        print(f"Correo: {email}")
        print(f"Teléfono: {telefono}")


        
        if not nombre or not email or not telefono:
            flash('Faltan campos requeridos.', 'danger')
            return redirect(url_for('auth.login'))

        cliente_existente = db.session.execute(
            db.select(Cliente).filter_by(email=email)
        ).scalar_one_or_none()

        if cliente_existente:
            flash(f'¡Bienvenido de vuelta, {cliente_existente.nombre_cliente}!', 'success')
            return redirect(url_for('auth.login')) 
        else:
            try:
                nuevo_cliente = Cliente(
                    nombre_cliente=nombre, 
                    email=email, 
                    telefono=telefono
                )
                db.session.add(nuevo_cliente)
                db.session.commit()
                
                flash(f'¡Cuenta creada y sesión iniciada para {nombre}!', 'success')
                return redirect(url_for('auth.login')) 
                
            except IntegrityError:
                db.session.rollback()
                flash('Error al registrar. El correo podría ya estar en uso.', 'danger')
                return redirect(url_for('auth.login'))
            except Exception as e:
                db.session.rollback()
                flash(f'Ocurrió un error inesperado: {e}', 'danger')
                return redirect(url_for('auth.login'))