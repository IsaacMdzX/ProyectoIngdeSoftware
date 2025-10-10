from flask import Blueprint, render_template


main_bp = Blueprint('main', __name__)

@main_bp.route('/catalogo')
def catalogo():
    """
    Esta ruta mostrará el catálogo de tenis.
    """
    
    return render_template('public/catalogo_tenis.html')