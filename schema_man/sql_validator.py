import sqlglot
from sqlglot.errors import ParseError


def validate_sql(sql_schema: str, dialect: str):
    """
    Validate the given SQL schema using sqlglot.

    Args:
        sql_query (str): The SQL query to validate.
        dialect (str): The SQL dialect to use for validation.

    Returns:
        bool: True if the SQL query is valid, False otherwise.
    """
    try:

        tree = sqlglot.parse_one(sql_schema, read=dialect)

        return {
            "valid": True,
            #  "message": "SQL schema is valid.",
            "errors": [],
            "tree" : tree
        }

    except ParseError as error:
        return {
            "valid": False,
            #  "message": "SQL schema is invalid.",
            "errors": [str(error)],
            "tree" : None
        }

