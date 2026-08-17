from .sql_validator import validate_sql


def validate_schema(sql: str, dialect: str) -> dict:
    """Validate a SQL schema using the configured SQL dialect."""
    return validate_sql(sql, dialect)
