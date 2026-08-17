"""
This module defines the routes for the SQL validator API.
"""
from flask import Blueprint, jsonify, request

from .sql_validator import validate_sql

validator_bp = Blueprint('validator', __name__, url_prefix='/api')


@validator_bp.post('/validate')
def validate():
    data = request.get_json(silent=True) or {}
    schema = data.get("sql", "").strip()
    dialect = data.get("dialect", "sqlite")

    if not schema:
        return jsonify({
            "valid": False,
            "errors": ["Empty SQL"]
        }), 400

    result = validate_sql(schema, dialect)

    return jsonify({
        "valid": result["valid"],
        "errors": result["errors"],
    })
