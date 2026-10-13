from typing import override

from ..context import PipeLineContext
from ..filter import Filter


class ModelSchemaFilter(Filter):

    @override
    def apply(self, context: PipeLineContext) -> PipeLineContext:
        try:
            pass
        except Exception as e:
            raise


    def ast_to_low_case(self, ast):
        pass
