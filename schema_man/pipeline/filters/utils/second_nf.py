"""
Second normal form algorithm detecter

Requirements
    1. The table must be in first normal form.
    2. If the primary key is simple (a single column), the table automatically satisfies second normal form.
    3. If the primary key is composite, look for attributes that depend on only part of the key. Those columns must be moved to a separate table.
"""

from .alerts import Alert, AlertColor
from .table_classes import Table


class SecondNormalFormDetecter:
    @staticmethod
    def is_in_first_normal_form(alerts: list[Alert]) -> bool:
        for alert in alerts:
            if alert.blocks_pipeline:
                return False
        return True

    @staticmethod
    def have_functional_dependencies(table: Table) -> bool:
        if table.get_functional_dependencies():
            return True
        return False

    @staticmethod
    def look_atributes_depending_on_a_part_of_pk(table: Table) -> list[Alert]:
        """Type of alert: green or red"""
        alerts: list[Alert] = []
        pk_columns = set(table.primary_key.columns)

        for fd in table.functional_dependencies:
            determinant = set(fd.determinant)

            # A partial dependency needs a proper non-empty subset of the PK
            # as determinant, plus at least one dependent column outside the
            # key (a non-prime attribute). Dependencies on the whole key or
            # between prime attributes are not partial dependencies.
            depends_on_part_of_key = determinant and determinant < pk_columns
            has_non_prime_column = set(fd.dependent) - pk_columns

            if depends_on_part_of_key and has_non_prime_column:
                alerts.append(Alert(
                    AlertColor.RED,
                    "PARTIAL DEPENDENCY: "
                    f"({', '.join(fd.determinant)}) -> "
                    f"({', '.join(fd.dependent)})",
                    table.name,
                ))

        # Without a partial dependency the table satisfies second normal form.
        if not alerts:
            alerts.append(Alert(
                AlertColor.GREEN,
                "NO PARTIAL DEPENDENCIES (PASS 2NF)",
                table.name,
            ))
        return alerts

    @staticmethod
    def detect_second_nf(table: Table) -> list[Alert]:
        alerts: list[Alert] = []

        # Requirement 1: without a PK the table is not even in first normal
        # form; the first normal form detector already reported it.
        if table.primary_key is None:
            return alerts

        # Requirement 2: a simple PK satisfies second normal form by itself,
        # so there are no partial dependencies to look for.
        if len(table.primary_key.columns) < 2:
            alerts.append(Alert(
                AlertColor.GREEN,
                "TABLE WITH SIMPLE PK (PASS 2NF)",
                table.name,
            ))
            return alerts

        # Requirement 3: partial dependencies can only be checked when the
        # functional dependencies are declared. Without them a gray alert is
        # reported and the evaluation continues with the next normal form.
        if not SecondNormalFormDetecter.have_functional_dependencies(table):
            alerts.append(Alert(
                AlertColor.GRAY,
                "TABLE DOES NOT HAVE FUNCTIONAL DEPENDENCIES",
                table.name,
            ))
            return alerts

        # Requirement 3: with a composite PK and declared FDs, every
        # attribute must depend on the whole key.
        alerts.extend(
            SecondNormalFormDetecter.look_atributes_depending_on_a_part_of_pk(
                table
            )
        )
        return alerts
