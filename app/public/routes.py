from flask import Blueprint, render_template
from ..extensions import db
from .models import Tenis, Gorra, Playera

public_bp = Blueprint('public', __name__, template_folder='templates')

@public_bp.route('/')
def index():
    tenis = db.session.execute(db.select(Tenis)).scalars().all()
    return render_template('public/Catalogo_Tenis.html', tenis=tenis)

@public_bp.route('/gorras')
def catalogo_gorras():
    gorras = db.session.execute(db.select(Gorra)).scalars().all()
    return render_template('public/Catalogo_Gorras.html', gorras=gorras)

@public_bp.route('/playeras')
def catalogo_playeras():
    playeras = db.session.execute(db.select(Playera)).scalars().all()
    return render_template('public/Catalogo_Playeras.html', playeras=playeras)