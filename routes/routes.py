from flask import Blueprint, render_template, abort
from models.models import Post  


main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def index():
    posts = Post.get_all()
    return render_template("index.html", posts=posts)

@main_bp.route("/p/<string:slug>/")
def show_post(slug):
    post = Post.get_by_slug(slug)
    if post is None:
        abort(404)
    return render_template("post_view.html", post=post)

@main_bp.route('/clientes')
def clientes():
    
    return render_template('clientes.html')

