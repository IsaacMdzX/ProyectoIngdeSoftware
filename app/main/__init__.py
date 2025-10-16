from flask import Blueprint, render_template


main_bp = Blueprint('main', __name__)


@main_bp.route('/catalogo')
def catalogo():
    # por compatibilidad dejamos /catalogo apuntando a tenis
    return render_template('public/catalogo_tenis.html')


@main_bp.route('/catalogo/tenis')
def tenis():
    return render_template('public/catalogo_tenis.html')


@main_bp.route('/catalogo/playeras')
def playeras():
    return render_template('public/Catalogo_Playeras.html')


@main_bp.route('/catalogo/gorras')
def gorras():
    return render_template('public/Catalogo_Gorras.html')


@main_bp.route('/carrito')
def carrito():
    return render_template('public/carrito.html')


@main_bp.route('/metodo_pago')
def metodo_pago():
    return render_template('public/metodo_pago.html')


@main_bp.route('/datos_pago')
def datos_pago():
    return render_template('public/Datos_pago.html')


@main_bp.route('/pago_exitoso')
def pago_exitoso():
    return render_template('public/pago_exitoso.html')


@main_bp.route('/resultados')
def resultados():
    # búsqueda simple; más adelante pasaremos resultados reales
    return render_template('public/resultados.html')