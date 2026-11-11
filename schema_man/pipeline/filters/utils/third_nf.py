"""
Third normal form algorithm detecter

Requirements:
    1. The table must be in second normal form.
    2. No attribute in the table may depend on another attribute that is not part of the primary key.
"""

from .alerts import Alert, AlertColor
from .table_classes import Table


class ThirdNormalFormDetecter:
    @staticmethod
    def is_in_second_normal_form(alerts: list[Alert]):
        for a in alerts:
            if a.blocks_pipeline:
                return False
        return True

    @staticmethod
    def detect_third_nf(table: Table) -> list[Alert]:
        """Detect transitive dependencies
        In the algorithm there is an exception: candidate keys
        candidate keys are for BCNF yet if you don't specify that case
        in third nf it's probably to find a fake transitive dependencies
        in this part of the system.
        """
        # Without declared functional dependencies there is nothing to check:
        # report the missing information and keep the flow going.
        if not table.get_functional_dependencies():
            return [
                Alert(
                    AlertColor.GRAY,
                    "CANNOT CHECK TRANSITIVE DEPENDENCIES WITHOUT FUNCTIONAL "
                    "DEPENDENCIES",
                    table.name,
                )
            ]

        alerts: list[Alert] = []
        pk_columns = set(table.primary_key.columns)
        columns = {c.name for c in table.columns}
        for fd in table.get_functional_dependencies():
            pk_in_fd_determinant: bool = any(
                coincidence in fd.determinant for coincidence in pk_columns
            )

            # Verify if the FD is candidate key
            is_candidate_key = False
            fd_columns = set(fd.determinant) | set(fd.dependent)
            if fd_columns >= columns:
                is_candidate_key = True

            # Detect transitive dependencies
            if pk_in_fd_determinant or is_candidate_key == True:
                pass
            else:
                alerts.append(
                    Alert(
                        AlertColor.RED,
                        f"TRANSITIVE DEPENDENCY ON \n\t{fd}",
                        table.name
                    )
                )

        if len(alerts) == 0:
            alerts.append(
                Alert(
                    AlertColor.GREEN,
                    "NO TRANSITIVE DEPENDENCIES FOUND",
                    table.name
                )
            )

        return alerts
