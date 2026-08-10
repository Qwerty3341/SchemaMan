from flask import Blueprint, render_template

bp = Blueprint('main', __name__)
manual_bp = Blueprint('manual', __name__, url_prefix='/manual')
about_bp = Blueprint('about', __name__, url_prefix='/about')


@bp.route('/')
def normalizator():
    return render_template('normalizator.html')


@manual_bp.route('/')
def manual_index():
    return render_template('manual.html')


@about_bp.route('/')
def about_index():
    return render_template('about.html')
