from typing import override

from schema_man.pipeline.context import PipeLineContext
from schema_man.pipeline.filters.utils.third_nf import ThirdNormalFormDetecter
from ..filter import Filter
from .utils.first_nf import FirstNormalFormDetecter
from .utils.second_nf import SecondNormalFormDetecter

# Normalization levels in increasing order. A detector only runs when the
# requested target reaches its level.
NORMALIZATION_ORDER = ("NF1", "NF2", "NF3", "BCNF", "NF4", "NF5")


def reaches_level(target: str, level: str) -> bool:
    """Tell whether normalizing up to `target` includes `level`."""
    if target not in NORMALIZATION_ORDER:
        raise ValueError(
            f"Unsupported normalization level {target!r}; expected one of: "
            f"{', '.join(NORMALIZATION_ORDER)}"
        )
    return NORMALIZATION_ORDER.index(target) >= NORMALIZATION_ORDER.index(level)


class NFDetectionFilter(Filter):
    @override
    def apply(self, context: PipeLineContext) -> PipeLineContext:
        if context.schema is None:
            raise ValueError("SCHEMA MUST BE MODELED BEFORE NF DETECTION")

        evaluate_second_nf = reaches_level(context.target_normal_form, "NF2")

        for table in context.schema:
            first_nf_alerts = FirstNormalFormDetecter.detect_first_nf(table)
            context.violations.extend(first_nf_alerts)

            if not evaluate_second_nf:
                continue

            # Requirement 1 of the second normal form: the table must be in
            # first normal form. A blocking alert (RED/GRAY) stops the
            # evaluation of this table in the higher normal forms.
            if not SecondNormalFormDetecter.is_in_first_normal_form(first_nf_alerts):
                continue

            second_nf_alerts = SecondNormalFormDetecter.detect_second_nf(table)

            # Third Normal form
            if not ThirdNormalFormDetecter.is_in_second_normal_form(second_nf_alerts):
                continue

            context.violations.extend(
                ThirdNormalFormDetecter.detect_third_nf(table)
            )
        return context
