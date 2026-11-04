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
        report_tables: list[dict] = []
        separator = "-------------------------------------------------------------------"

        for table in context.schema:
            table_alerts = alerts_by_table.get(table.name, [])
            # A red alert fails the level. A gray alert stops the evaluation
            # without a verdict, so the level cannot be decided.
            if any(alert.color == AlertColor.RED for alert in table_alerts):
                header_status, status = "[ FAILS ]", "fails"
            elif any(alert.color == AlertColor.GRAY for alert in table_alerts):
                header_status, status = "[ INDETERMINATE ]", "indeterminate"
            else:
                header_status, status = "[ PASSES ]", "passes"

            report_lines.extend([
                separator,
                f"Table: {table.name}\tEvaluated level: "
                f"{context.target_normal_form}\t{header_status}",
                separator,
            ])

            for alert in table_alerts:
                report_lines.append(
                    f"*\t{context.target_normal_form}\t{alert.message}\t{alert.color}"
                )

            # Structured copy for the front-end (same data, with colors)
            report_tables.append({
                "name": table.name,
                "evaluated_level": context.target_normal_form,
                "status": status,
                "alerts": [
                    {"color": alert.color, "message": alert.message}
                    for alert in table_alerts
                ],
            })

        context.report = "\n".join(report_lines)
        context.report_tables = report_tables
        return context
