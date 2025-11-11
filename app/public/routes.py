from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
import os
from ..extensions import db
from ..auth.models import Cliente, Admin
from .models import Tenis, Gorra, Playera
from urllib.parse import urljoin
import logging

public_bp = Blueprint('public', __name__, template_folder='templates')


def _resolve_image_url(filename: str):
    """Return best static URL for a product image: small thumb -> original -> placeholder."""
    try:
        if not filename:
            return url_for('static', filename='images/placeholder.svg')
        # paths on disk
        thumb_rel = os.path.join('images', 'product_images', 'thumbs', 'small', filename)
        orig_rel = os.path.join('images', 'product_images', filename)
        thumb_path = os.path.join(current_app.static_folder, thumb_rel)
        orig_path = os.path.join(current_app.static_folder, orig_rel)
        if os.path.exists(thumb_path):
            return url_for('static', filename=thumb_rel)
        if os.path.exists(orig_path):
            return url_for('static', filename=orig_rel)
    except Exception:
        # any failure, fall back to placeholder
        current_app.logger.debug('Error resolviendo image_url para %s', filename)
    return url_for('static', filename='images/placeholder.svg')

@public_bp.route('/')
def index():
    tenis = db.session.execute(db.select(Tenis)).scalars().all()
    # attach resolved image URL to each product for simpler templates
    for t in tenis:
        try:
            fn = getattr(t, 'image_filename', None)
            setattr(t, 'image_url', _resolve_image_url(fn))
        except Exception:
            setattr(t, 'image_url', url_for('static', filename='images/placeholder.svg'))
    return render_template('public/Catalogo_Tenis.html', tenis=tenis)

@public_bp.route('/gorras')
def catalogo_gorras():
    gorras = db.session.execute(db.select(Gorra)).scalars().all()
    for g in gorras:
        try:
            fn = getattr(g, 'image_filename', None)
            setattr(g, 'image_url', _resolve_image_url(fn))
        except Exception:
            setattr(g, 'image_url', url_for('static', filename='images/placeholder.svg'))
    return render_template('public/Catalogo_Gorras.html', gorras=gorras)

@public_bp.route('/playeras')
def catalogo_playeras():
    playeras = db.session.execute(db.select(Playera)).scalars().all()
    for p in playeras:
        try:
            fn = getattr(p, 'image_filename', None)
            setattr(p, 'image_url', _resolve_image_url(fn))
        except Exception:
            setattr(p, 'image_url', url_for('static', filename='images/placeholder.svg'))
    return render_template('public/Catalogo_Playeras.html', playeras=playeras)

# ---------- Detalle de producto ----------
@public_bp.route('/producto/<string:tipo>/<int:id>')
def producto_detalle(tipo, id):
    tipo_lower = tipo.lower()
    producto = None
    nombre = None
    precio = None
    descripcion = None

    try:
        if tipo_lower == 'tenis':
            producto = db.session.get(Tenis, id)
            if producto:
                nombre = producto.nombre_tenis
                precio = producto.precio
                descripcion = producto.descripcion
        elif tipo_lower == 'playera':
            producto = db.session.get(Playera, id)
            if producto:
                nombre = producto.nombre_playera
                precio = producto.precio
                descripcion = producto.descripcion
        elif tipo_lower == 'gorra':
            producto = db.session.get(Gorra, id)
            if producto:
                nombre = producto.nombre_gorra
                precio = producto.precio
                descripcion = producto.descripcion
        else:
            flash('Tipo de producto no válido.', 'danger')
            return redirect(url_for('public.index'))
    except Exception:
        producto = None

    if not producto:
        flash('Producto no encontrado.', 'warning')
        return redirect(url_for('public.index'))

    # imagen si existe: compute image_url (thumb -> original -> placeholder)
    try:
        image_filename = getattr(producto, 'image_filename', None)
        image_url = _resolve_image_url(image_filename)
    except Exception:
        image_url = url_for('static', filename='images/placeholder.svg')

    return render_template('public/producto_detalle.html',
                           tipo=tipo_lower,
                           id_producto=id,
                           nombre=nombre,
                           precio=precio,
                           descripcion=descripcion,
                           image_url=image_url)

# ---------- Carrito ----------
def _cart_init():
    if 'carrito' not in session:
        session['carrito'] = []

@public_bp.route('/carrito')
def ver_carrito():
    _cart_init()
    items = session.get('carrito', [])
    total = sum(i['precio'] * i['cantidad'] for i in items)
    return render_template('public/carrito.html', items=items, total=total)

@public_bp.route('/carrito/agregar', methods=['POST'])
def agregar_al_carrito():
    # Requiere inicio de sesión para agregar productos
    if not session.get('user_id'):
        flash('Debes iniciar sesión para agregar productos al carrito.', 'warning')
        next_url = request.referrer or url_for('public.index')
        return redirect(url_for('auth.login', next=next_url))
    _cart_init()
    tipo = request.form.get('tipo', '').lower()
    id_producto = request.form.get('id_producto', type=int)
    cantidad = request.form.get('cantidad', default=1, type=int)

    if cantidad <= 0 or not id_producto:
        flash('Datos inválidos para agregar al carrito.', 'danger')
        return redirect(request.referrer or url_for('public.index'))

    # Obtener datos del producto
    producto = None
    nombre = None
    precio = None
    if tipo == 'tenis':
        producto = db.session.get(Tenis, id_producto)
        if producto:
            nombre = producto.nombre_tenis
            precio = float(producto.precio)
    elif tipo == 'playera':
        producto = db.session.get(Playera, id_producto)
        if producto:
            nombre = producto.nombre_playera
            precio = float(producto.precio)
    elif tipo == 'gorra':
        producto = db.session.get(Gorra, id_producto)
        if producto:
            nombre = producto.nombre_gorra
            precio = float(producto.precio)
    else:
        flash('Tipo de producto no válido.', 'danger')
        return redirect(request.referrer or url_for('public.index'))

    if not producto:
        flash('Producto no encontrado.', 'warning')
        return redirect(request.referrer or url_for('public.index'))

    # Si ya existe en carrito, aumentar cantidad
    for item in session['carrito']:
        if item['tipo'] == tipo and item['id_producto'] == id_producto:
            item['cantidad'] += cantidad
            session.modified = True
            break
    else:
        session['carrito'].append({
            'tipo': tipo,
            'id_producto': id_producto,
            'nombre': nombre,
            'precio': precio,
            'cantidad': cantidad
        })
        session.modified = True
    return redirect(url_for('public.ver_carrito'))

@public_bp.route('/carrito/eliminar/<string:tipo>/<int:id_producto>', methods=['POST'])
def eliminar_del_carrito(tipo, id_producto):
    # Requiere inicio de sesión para modificar el carrito
    if not session.get('user_id'):
        flash('Debes iniciar sesión para modificar el carrito.', 'warning')
        next_url = request.referrer or url_for('public.ver_carrito')
        return redirect(url_for('auth.login', next=next_url))
    _cart_init()
    tipo = tipo.lower()
    session['carrito'] = [i for i in session['carrito'] if not (i['tipo'] == tipo and i['id_producto'] == id_producto)]
    session.modified = True
    flash('Producto eliminado del carrito.', 'info')
    return redirect(url_for('public.ver_carrito'))

# ---------- Checkout (pago) ----------
@public_bp.route('/checkout')
def checkout():
    # Requiere inicio de sesión para proceder al pago
    if not session.get('user_id'):
        flash('Debes iniciar sesión para proceder al pago.', 'warning')
        next_url = url_for('public.checkout')
        return redirect(url_for('auth.login', next=next_url))
    # Página inicial del flujo de pago
    items = session.get('carrito', [])
    total = sum(i['precio'] * i['cantidad'] for i in items)
    return render_template('metodo_pago.html', total=total, items=items)

@public_bp.route('/checkout/datos')
def checkout_datos():
    # Requiere inicio de sesión para proceder al pago
    if not session.get('user_id'):
        flash('Debes iniciar sesión para proceder al pago.', 'warning')
        next_url = url_for('public.checkout_datos')
        return redirect(url_for('auth.login', next=next_url))
    items = session.get('carrito', [])
    if not items:
        flash('Tu carrito está vacío.', 'warning')
        return redirect(url_for('public.ver_carrito'))
    total = sum(i['precio'] * i['cantidad'] for i in items)
    return render_template('Datos_pago.html', total=total)

@public_bp.route('/checkout/exito')
def checkout_exito():
    # Requiere inicio de sesión para proceder al pago
    if not session.get('user_id'):
        flash('Debes iniciar sesión para proceder al pago.', 'warning')
        next_url = url_for('public.checkout_exito')
        return redirect(url_for('auth.login', next=next_url))
    # Preparar datos para mostrar en éxito antes de limpiar carrito
    items = session.get('carrito', [])
    total = sum(i['precio'] * i['cantidad'] for i in items) if items else 0.0
    source = request.args.get('source')  # e.g., 'transfer'
    whatsapp_phone = current_app.config.get('WHATSAPP_PHONE')
    # Datos del usuario para mensaje de WhatsApp
    user_name = session.get('user_name')
    role = session.get('role')
    user_email = None
    try:
        if role == 'cliente' and session.get('user_id'):
            c = db.session.get(Cliente, session['user_id'])
            user_email = c.email if c else None
        elif role == 'admin' and session.get('user_id'):
            a = db.session.get(Admin, session['user_id'])
            user_email = a.correo if a else None
    except Exception:
        user_email = None
    # Generar un código/folio simple del pedido (no persistente)
    from datetime import datetime
    order_code = f"PED-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    # Vaciar carrito al llegar a la página de pago exitoso
    session['carrito'] = []
    session.modified = True
    return render_template(
        'pago_exitoso.html',
        total=total,
        source=source,
        whatsapp_phone=whatsapp_phone,
        user_name=user_name,
        user_email=user_email,
        order_code=order_code,
    )

# ---------- Integraciones de pago externas ----------
def _carrito_items():
    return session.get('carrito', [])

@public_bp.route('/debug/mp')
def debug_mp():
    """Ruta de diagnóstico simple para verificar si el servidor ve MP_ACCESS_TOKEN."""
    try:
        tok = (current_app.config.get('MP_ACCESS_TOKEN')
               or os.environ.get('MP_ACCESS_TOKEN'))
        msg = f"MP_ACCESS_TOKEN presente: {bool(tok)}"
    except Exception:
        msg = "MP_ACCESS_TOKEN presente: False"
    return msg, 200, {"Content-Type": "text/plain; charset=utf-8"}


@public_bp.route('/checkout/pagar/<string:provider>')
def checkout_pagar(provider: str):
    if not session.get('user_id'):
        flash('Debes iniciar sesión para proceder al pago.', 'warning')
        return redirect(url_for('auth.login', next=url_for('public.checkout_pagar', provider=provider)))

    items = _carrito_items()
    if not items:
        flash('Tu carrito está vacío.', 'warning')
        return redirect(url_for('public.ver_carrito'))

    provider = provider.lower()
    if provider in ('mp', 'mercadopago', 'mercado-pago', 'mercado'):  # Mercado Pago
        # Intentar obtener desde config primero y luego desde el entorno
        mp_token = current_app.config.get('MP_ACCESS_TOKEN') or os.environ.get('MP_ACCESS_TOKEN')
        if not mp_token:
            flash('Mercado Pago no está configurado (falta MP_ACCESS_TOKEN).', 'danger')
            return redirect(url_for('public.checkout'))
        try:
            import importlib
            mp_mod = importlib.import_module('mercadopago')
            SDK = getattr(mp_mod, 'SDK')
        except Exception:
            flash('SDK de Mercado Pago no instalado. Instala el paquete "mercadopago".', 'danger')
            return redirect(url_for('public.checkout'))

        sdk = SDK(mp_token)
        preference_items = []
        for i in items:
            preference_items.append({
                "title": i['nombre'],
                "quantity": int(i['cantidad']),
                "currency_id": "MXN",
                "unit_price": float(i['precio'])
            })
        total_amount = sum(x['quantity'] * x['unit_price'] for x in preference_items)
        if total_amount <= 0:
            flash('El total del carrito debe ser mayor a $0.00 para procesar el pago.', 'warning')
            return redirect(url_for('public.ver_carrito'))
        # Construir back_urls con base pública si está configurada, o usar el host actual
        external_base = (current_app.config.get('EXTERNAL_BASE_URL')
                         or os.environ.get('EXTERNAL_BASE_URL'))
        if external_base:
            if not external_base.endswith('/'):
                external_base = external_base + '/'
            path_success = url_for('public.payment_return', provider='mercadopago', status='success', _external=False).lstrip('/')
            path_failure = url_for('public.payment_return', provider='mercadopago', status='failure', _external=False).lstrip('/')
            path_pending = url_for('public.payment_return', provider='mercadopago', status='pending', _external=False).lstrip('/')
            back_success = urljoin(external_base, path_success)
            back_failure = urljoin(external_base, path_failure)
            back_pending = urljoin(external_base, path_pending)
        else:
            back_success = url_for('public.payment_return', provider='mercadopago', status='success', _external=True)
            back_failure = url_for('public.payment_return', provider='mercadopago', status='failure', _external=True)
            back_pending = url_for('public.payment_return', provider='mercadopago', status='pending', _external=True)
        preference_data = {
            "items": preference_items,
      }
        # Incluir back_urls + auto_return solo si:
        #  - Token sandbox (no APP_USR), o
        #  - EXTERNAL_BASE_URL comienza con https:// (dominio público seguro)
        is_prod_token = bool(mp_token and mp_token.startswith('APP_USR'))
        external_base = (current_app.config.get('EXTERNAL_BASE_URL') or os.environ.get('EXTERNAL_BASE_URL'))
        has_https_base = bool(external_base and external_base.lower().startswith('https://'))
        has_http_base = bool(external_base and external_base.lower().startswith('http://'))
        if (not is_prod_token) or has_https_base:
            preference_data.update({
                "back_urls": {
                    "success": back_success,
                    "failure": back_failure,
                    "pending": back_pending
                },
                "auto_return": "approved"
            })
        else:
            # Fallback: token producción + entorno local sin HTTPS público.
            # Evitar auto_return para no gatillar validación de back_url.success
            # MP igualmente devolverá init_point y permitirá continuar desde su UI.
            preference_data.update({
                # "back_urls": { ... }  # opcionalmente podríamos omitirlas por completo
            })
            # Aviso para el usuario (se mostrará al volver del flujo o en la próxima navegación)
            if is_prod_token and (not external_base or has_http_base):
                flash('Usas un token de producción sin un dominio HTTPS público. Se omitieron back_urls/auto_return. Configura EXTERNAL_BASE_URL con https:// para retorno automático.', 'info')
        try:
            result = sdk.preference().create(preference_data)
            # Log full response for debugging: status, response body and init_point if present
            try:
                current_app.logger.debug(f"MercadoPago preference raw result: {result}")
            except Exception:
                # Fallback to standard logging if current_app is not available for some reason
                logging.debug("MercadoPago preference raw result: %r", result)
            resp = result.get("response", {}) if isinstance(result, dict) else {}
            status_code = result.get("status") if isinstance(result, dict) else None
            init_point = resp.get("init_point") or resp.get("sandbox_init_point")
            if init_point:
                return redirect(init_point)
            # Sin init_point: mostrar detalles para diagnóstico
            message = resp.get("message") or resp.get("error") or "Respuesta inválida"
            cause = resp.get("cause")
            if isinstance(cause, list) and cause:
                message = f"{message} - {cause[0].get('code', '')}: {cause[0].get('description', '')}"
            if status_code and message:
                flash(f"No se pudo obtener el enlace de pago (HTTP {status_code}): {message}", 'danger')
            else:
                flash('No se pudo obtener el enlace de pago de Mercado Pago.', 'danger')
            # Sugerencias útiles según el entorno
            tip = 'Tip: '
            if mp_token and mp_token.startswith('APP_USR'):
                tip += 'Tu token es de producción (APP_USR). Mercado Pago suele exigir back_urls HTTPS públicas. Configura EXTERNAL_BASE_URL=https://tu-dominio-o-tunnel y vuelve a intentar.'
            else:
                tip += 'Para pruebas locales usa un Access Token de Sandbox (TEST-...) o configura EXTERNAL_BASE_URL con un dominio HTTPS (por ejemplo, un túnel tipo ngrok) y vuelve a intentar.'
            flash(tip, 'info')
            return redirect(url_for('public.checkout'))
        except Exception as e:
            flash(f'Error creando la preferencia de Mercado Pago: {e}', 'danger')
            return redirect(url_for('public.checkout'))

    else:
        flash('Proveedor de pago no soportado.', 'danger')
        return redirect(url_for('public.checkout'))

@public_bp.route('/checkout/retorno/<string:provider>')
def payment_return(provider: str):
    provider = provider.lower()
    status = request.args.get('status') or request.args.get('collection_status')
    if provider in ('mp', 'mercadopago', 'mercado-pago', 'mercado'):
        if status == 'success' or status == 'approved':
            # Limpiar carrito y mostrar éxito
            session['carrito'] = []
            session.modified = True
            flash('Pago aprobado por Mercado Pago.', 'success')
            return redirect(url_for('public.checkout_exito'))
        elif status == 'pending':
            flash('Pago pendiente en Mercado Pago.', 'warning')
            return redirect(url_for('public.ver_carrito'))
        else:
            flash('Pago cancelado o fallido en Mercado Pago.', 'danger')
            return redirect(url_for('public.ver_carrito'))
    else:
        flash('Proveedor de pago no soportado.', 'danger')
        return redirect(url_for('public.ver_carrito'))