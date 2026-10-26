from typing import override

import sqlglot

from ..context import PipeLineContext
from ..filter import Filter


class ParseSqlFilter(Filter):
    @override
    def apply(self, context: PipeLineContext) -> PipeLineContext:
        if not context.sql.strip():
            raise ValueError("SQL must not be empty")

        try:
            statements = sqlglot.parse(context.sql, dialect=context.dialect)
        except sqlglot.ParseError as e:
            raise ValueError(f"SQL with syntax errors: {e}") from e

        context.sql_ast = [
            statement for statement in statements if statement is not None
        ]
        return context
