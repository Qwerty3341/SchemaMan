"""
Boyce-Codd Normal Form

Requirements:
    1. The table must be in third normal form.
    2. Every determinant must be a candidate key.
"""

from .alerts import Alert, AlertColor
from .table_classes import Table


class BoyceCoddNormalFormDetecter:
    @staticmethod
    def is_in_third_normal_form(alerts: list[Alert]):
        for a in alerts:
            if a.blocks_pipeline:
                return False
        return True

    @staticmethod
    def look_if_every_determinant_is_candidate_key(table: Table):
        alerts: list[Alert] = []
        pk_columns = set(table.primary_key.columns)
        columns = {c.name for c in table.columns}

        for fd in table.get_functional_dependencies():
            is_candidate_key = False
            fd_columns = set(fd.determinant) | set(fd.dependent)
            if fd_columns >= columns:
                is_candidate_key = True

            if is_candidate_key:
                alerts.append(
                    Alert(
                        AlertColor.GREEN,
                        f"Determinant {fd.determinant} is candidate key",
                        table.name
                    )
                )
            else:
                alerts.append(
                    Alert(
                        AlertColor.RED,
                        f"Determinant {fd.determinant} is not a candidat key",
                        table.name
                    )
                )
        return alerts
