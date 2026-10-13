from typing import override

from sqlglot import parse
from sqlglot import ParseError

from ..context import PipeLineContext
from ..filter import Filter


class ParseSqlFilter(Filter):

    @override
    def apply(self, context: PipeLineContext) -> PipeLineContext:
        if not context.sql.strip():
            raise ValueError("SQL must not be empty")

        try:
            context.ast = parse(context.sql, read=context.dialect)

        except ParseError as e:
            raise ValueError(
                f"Could not parse SQL with dialect '{context.dialect}'"
            ) from e

        return context
