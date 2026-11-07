"""
Fourth normal form

Requirements:
    1. The table must be in Boyce-Codd normal form.
    2. The table must not contain more than one independent multivalued dependency.
"""

from .alerts import Alert, AlertColor
from .table_classes import Table


class FourthNormalFormDetecter:
    @staticmethod
    def is_in_bcnf(alerts: list[Alert]):
        for a in alerts:
            if a.blocks_pipeline:
                return False
        return True

    @staticmethod
    def there_is_mvd(table: Table):
        if table.get_multivalued_dependencies():
            return True
        else:
            return False

    @staticmethod
    def check_the_mvd(table: Table):
        pass

    @staticmethod
    def detect_fourth_nf(table: Table):
        alerts: list[Alert] = []
        if not FourthNormalFormDetecter.there_is_mvd(table):
            alerts.append(
                Alert(
                    AlertColor.GRAY,
                    "NO MVD IN THE TABLE",
                    table.name
                )
            )
            return alerts
        return alerts
