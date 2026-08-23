import sqlglot
from sqlglot import exp
from sqlglot.errors import ErrorLevel, ParseError


def validate_sql(sql_schema: str, dialect: str):
    """Validate the syntax and basic structure of a SQL schema."""
    try:
        trees = sqlglot.parse(
            sql_schema,
            read=dialect,
            error_level=ErrorLevel.RAISE,
        )

        if not trees:
            return {
                "valid": False,
                "errors": ["No SQL statement was found."],
                "tree": None,
            }

        errors = []

        for index, tree in enumerate(trees, start=1):
            if not isinstance(tree, exp.Create):
                errors.append(f"Statement {index}: expected CREATE TABLE.")
                continue

            if tree.args.get("kind") != "TABLE":
                errors.append(
                    f"Statement {index}: expected a table definition."
                )
                continue

            schema = tree.this

            if not isinstance(schema, exp.Schema):
                errors.append(
                    f"Statement {index}: missing parentheses around columns."
                )
                continue

            columns = schema.expressions

            if not columns:
                errors.append(
                    f"Statement {index}: the table must have at least one column."
                )
                continue

            for column in columns:
                if not isinstance(column, exp.ColumnDef):
                    errors.append(
                        f"Statement {index}: invalid column definition."
                    )

        return {
            "valid": not errors,
            "errors": errors,
            "tree": trees if not errors else None,
        }

    except ParseError as error:
        return {
            "valid": False,
            "errors": [str(error)],
            "tree": None,
        }
