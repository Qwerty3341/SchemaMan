from typing import override

from ..context import PipeLineContext
from ..filter import Filter
from .utils.alerts import Alert, AlertColor

"""
Final Filter this will send the format alerts
obtained in the previous filter (nf_detection.py)
"""


class ReportFilter(Filter):
    @override
    def apply(self, context: PipeLineContext) -> PipeLineContext:
        if context.schema is None:
            raise ValueError(
                "Schema must be modeled before creating the report")

        alerts_by_table: dict[str, list[Alert]] = {}
        for alert in context.violations:
            alerts_by_table.setdefault(
                alert.associated_table, []).append(alert)

        report_lines: list[str] = []
        separator = "-------------------------------------------------------------------"

        for table in context.schema:
            table_alerts = alerts_by_table.get(table.name, [])
            has_red_alert = any(
                alert.color == AlertColor.RED for alert in table_alerts
            )
            status = "[ FAILS ]" if has_red_alert else "[ PASSES ]"

            report_lines.extend([
                separator,
                f"Table: {table.name}\tEvaluated level: "
                f"{context.target_normal_form}\t{status}",
                separator,
            ])

            for alert in table_alerts:
                report_lines.append(
                    f"*\t{context.target_normal_form}\t{alert.message}\t{alert.color}"
                )

        context.report = "\n".join(report_lines)
        return context
