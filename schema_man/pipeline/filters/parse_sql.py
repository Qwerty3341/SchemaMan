from typing import override
from ..context import PipeLineContext
from ..filter import Filter
import sqlglot


class ParseSqlFilter(Filter):
    @override
    def apply(self, context: PipeLineContext) -> PipeLineContext:
        if not context.sql.strip():
            raise ValueError("SQL must not be empty")

        try:
            sqlglot.parse_one(context.sql, dialect=context.dialect)
        except sqlglot.ParseError as e:
            raise ValueError(f"SQL with syntax errors: {e}") from e

        return context
