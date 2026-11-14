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
    2. If all the keys are simple put green alert
    3. Each join dependency must be implied by the keys
        3.1. Extract the JD
        3.2. If not a JD declared
            3.2.1 If the PK reaches all the columns put Yellow
            3.2.2 Otherwise put gray (NO JD DECLARED)
        3.3 For each JD
            3.3.1. Check if the union of the components results in the original table (Green or Gray)
            3.3.2. If one component contains all the columns drop the green
            3.3.3. Else, merge the components: if two components share columns and those columns are both
                    superkey, can put together in one component. Repeat untill there is nothing to join.
            3.3.4. If that component reaches all the columns drop green alert (JD is deduced by the keys)
            3.3.5. Else, drop a red alert (JOIN DEPENDENCY NOT IMPLIED BY THE KEYS)
"""

from .alerts import Alert, AlertColor
from .table_classes import Table


class FifthNormalFormDetecter:
    @staticmethod
    def is_in_fourth_nf(alerts: list[Alert]):
        for a in alerts:
            if a.blocks_pipeline:
                return False
        return True

    @staticmethod
    def from_thirth_to_fifth(table: Table) -> bool:
        primary_key = table.get_primary_key()
        primary_key_is_simple = (
            primary_key is not None and len(primary_key.columns) == 1
        )

        # Every UNIQUE constraint must be a single column key.
        unique_keys_are_simple = all(
            len(key.columns) == 1 for key in table.get_unique_keys()
        )

        for fd in table.get_functional_dependencies():
            if len(fd.determinant) != 1:
                return False

        return primary_key_is_simple and unique_keys_are_simple

    @staticmethod
    def detect_fifth_nf(table: Table) -> list[Alert]:
        if FifthNormalFormDetecter.from_thirth_to_fifth(table):
            return [
                Alert(
                    AlertColor.GREEN,
                    "ALL KEYS ARE SIMPLE (PASSES 5NF)",
                    table.name
                )
            ]

        return [
            Alert(
                AlertColor.RED,
                "THERE ARE COMPOSITE KEYS (NOT PASS 5NF)",
                table.name
            )
        ]
