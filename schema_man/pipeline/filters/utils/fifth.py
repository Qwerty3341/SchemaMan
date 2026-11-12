"""
Requirements:
    1. The table must be in fourth normal form.
    2. Every join dependency in the table must be implied by its candidate keys.

Problem:
    This system can not check the separations thought the process of normalization.
    It is designed to detect the compliance of normal forms.

Solution:
    Can use the candidate keys from BCNF
    1. If all candidate keys are simple, complies the 5nf
        1.1 Group pk
        1.2 Group the UNIQUE columns
        1.3 Group the determinant of each FD that reach all the columns (BCNF)
    2.If all the keys are simple put green alert
"""

from .alerts import Alert, AlertColor
from .table_classes import Table


class FifhNormalFormDetecter:
    @staticmethod
    def is_in_fourth_nf(alerts: list[Alert]):
        for a in alerts:
            if a.blocks_pipeline:
                return False
        return True

    @staticmethod
    def from_thirth_to_fifth(table: Table):
        group = [table.get_primary_key()]
        for column in table.get_columns():
            pass

    @staticmethod
    def detect_fifth_nf(table: Table):
        pass
