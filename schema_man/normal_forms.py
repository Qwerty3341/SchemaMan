from flask import Blueprint, render_template

nf_bp = Blueprint('nf', __name__, url_prefix='/nf')


@nf_bp.route('/nf1')
def nf1():
    return render_template('nf/nf1.html')


@nf_bp.route('/nf2')
def nf2():
    return render_template('nf/nf2.html')


@nf_bp.route('/nf3')
def nf3():
    return render_template('nf/nf3.html')


@nf_bp.route('/nf4')
def nf4():
    return render_template('nf/nf4.html')


@nf_bp.route('/nf5')
def nf5():
    return render_template('nf/nf5.html')
