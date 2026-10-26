from typing import override

from schema_man.pipeline.context import PipeLineContext
from ..filter import Filter
from .utils.first_nf import FirstNormalFormDetecter


class NFDetectionFilter(Filter):
    @override
    def apply(self, context: PipeLineContext) -> PipeLineContext:
        if context.schema is None:
            raise ValueError("Schema must be modeled before NF detection")

        for table in context.schema:
            context.violations.extend(
                FirstNormalFormDetecter.detect_first_nf(table)
            )

        return context
