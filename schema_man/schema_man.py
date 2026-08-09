from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort
bp = Blueprint('main', __name__)


@bp.route('/')
def normalizator():
    return render_template('app/normalizator.html')
