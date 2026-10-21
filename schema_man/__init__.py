import os

from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    from .schema_man import bp as main_bp, manual_bp, about_bp
    from .normal_forms import nf_bp
    from .api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(manual_bp)
    app.register_blueprint(nf_bp)
    app.register_blueprint(about_bp)
    app.register_blueprint(api_bp)

    return app
