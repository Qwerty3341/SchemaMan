from typing import override

from ..context import PipeLineContext
from ..filter import Filter


class ModelSchemaFilter(Filter):
    @override
    def apply(self, context: PipeLineContext) -> PipeLineContext:
        """Process the context and returns it"""
        raise NotImplementedError

    def schema_to_upper_case(self):
        pass

    def table_to_generic_syntax(self):
        pass

    def detect_table(self, line_of_schema):
        pass

    def model_schema(self):
        pass

    def get_table_name(self):
        pass

