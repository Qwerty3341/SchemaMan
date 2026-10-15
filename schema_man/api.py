from flask import Blueprint, jsonify, request

from .pipeline.context import PipeLineContext
from .pipeline.filters.parse_sql import ParseSqlFilter
from .pipeline.pipe import Pipe

api_bp = Blueprint("api", __name__, url_prefix="/api")

SUPPORTED_DIALECTS = {"sqlite", "mysql"}
SUPPORTED_NORMAL_FORMS = {"NF1", "NF2", "NF3", "BCNF", "NF4", "NF5"}


@api_bp.post("/parse-sql") # Web interface to ParseSqlFilter
def parse_sql():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(valid=False, error="Expect a JSON object"), 400

    sql = data.get("sql")
    dialect = data.get("dialect")
    normalization_level = data.get("normalization_level")

    if not isinstance(sql, str) or not sql.strip():
        return jsonify(valid=False, error="SQL must be a non-empty text"), 400

    if not isinstance(dialect, str) or not dialect.strip():
        return jsonify(valid=False, error="Dialect is required and must be text"), 400

    if not isinstance(normalization_level, str) or not normalization_level.strip():
        return jsonify(valid=False, error="Normalization level is required and must be text"), 400

    if dialect not in SUPPORTED_DIALECTS:
        return jsonify(valid=False, error=f"Unsupported dialect: {dialect}"), 400

    if normalization_level not in SUPPORTED_NORMAL_FORMS:
        return jsonify(valid=False, error=f"Unsupported normalization level: {normalization_level}"), 400

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
