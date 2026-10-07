from flask import Blueprint, jsonify, request

from .pipeline.context import PipeLineContext
from .pipeline.filters.parse_sql import ParseSqlFilter
from .pipeline.pipe import Pipe

api_bp = Blueprint("api", __name__, url_prefix="/api")

# Web interface to ParseSqlFilter


@api_bp.post("/parse-sql")
def parse_sql():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(valid=False, error="Se esperaba un objeto JSON"), 400

    sql = data.get("sql")
    dialect = data.get("dialect", "sqlite")
    normalization_level = data.get("normalization_level", "FN1")

    if not isinstance(sql, str):
        return jsonify(valid=False, error="SQL debe ser texto"), 400

    if not isinstance(dialect, str):
        return jsonify(valid=False, error="El dialecto debe ser texto"), 400

    if not isinstance(normalization_level, str):
        return jsonify(valid=False, error="El nivel de normalización debe ser texto"), 400

    context = PipeLineContext(
        sql=sql,
        dialect=dialect,
        target_normal_form=normalization_level,
    )

    pipeline = Pipe(filters=[ParseSqlFilter()])

    try:
        context = pipeline.run(context)
    except ValueError as error:
        return jsonify(valid=False, error=str(error)), 400

    return jsonify(valid=True)
