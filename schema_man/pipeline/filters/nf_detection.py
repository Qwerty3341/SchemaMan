from typing import override

from schema_man.pipeline.context import PipeLineContext
from schema_man.pipeline.filters.utils.bcnf import BoyceCoddNormalFormDetecter
from schema_man.pipeline.filters.utils.fourth_nf import FourthNormalFormDetecter
from schema_man.pipeline.filters.utils.third_nf import ThirdNormalFormDetecter
from ..filter import Filter
from .utils.first_nf import FirstNormalFormDetecter
from .utils.second_nf import SecondNormalFormDetecter

# Normalization levels in increasing order. A detector only runs when the
# requested target reaches its level.
NORMALIZATION_ORDER = ("NF1", "NF2", "NF3", "BCNF", "NF4", "NF5")


def reaches_level(target: str, level: str) -> bool:
    """Tell whether normalizing up to target includes level."""
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
        evaluate_third_nf = reaches_level(context.target_normal_form, "NF3")
        evaluate_bc_nf = reaches_level(context.target_normal_form, "BCNF")
        evaluate_fourth_nf = reaches_level(context.target_normal_form, "NF4")

        for table in context.schema:
            first_nf_alerts = FirstNormalFormDetecter.detect_first_nf(table)
            context.violations.extend(first_nf_alerts)

            if not evaluate_second_nf:
                continue

            # Requirement 1 of the second normal form: the table must be in
            # first normal form. Only a red alert blocks the evaluation of
            # this table in the higher normal forms; gray keeps going.
            if not SecondNormalFormDetecter.is_in_first_normal_form(first_nf_alerts):
                continue

            second_nf_alerts = SecondNormalFormDetecter.detect_second_nf(table)
            context.violations.extend(second_nf_alerts)

            # The third normal form is only part of the target when the
            # requested level reaches NF3.
            if not evaluate_third_nf:
                continue

            # Requirement 1 of the third normal form: the table must be in
            # second normal form.
            if not ThirdNormalFormDetecter.is_in_second_normal_form(second_nf_alerts):
                continue

            third_nf_alerts = ThirdNormalFormDetecter.detect_third_nf(table)
            context.violations.extend(third_nf_alerts)

            # BCNF
            if not evaluate_bc_nf:
                continue

            bcnf_alerts = BoyceCoddNormalFormDetecter.look_if_every_determinant_is_candidate_key(table)
            context.violations.extend(bcnf_alerts)

            # 4 NF
            if not evaluate_fourth_nf:
                continue

            # Requirement 1 of the fourth normal form: the table must be in
            # Boyce-Codd normal form.
            if not FourthNormalFormDetecter.is_in_bcnf(bcnf_alerts):
                continue

            fourth_nf_alerts = FourthNormalFormDetecter.detect_fourth_nf(table)
            context.violations.extend(fourth_nf_alerts)

        return context
