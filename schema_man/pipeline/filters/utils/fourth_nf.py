"""Fourth normal form

Requirements:
    1. The table must be in Boyce-Codd normal form.
    2. For every non-trivial multivalued dependency X ->> Y, X must be a superkey.

    An MVD X ->> Y is trivial if Y is a subset of X, or X v Y = R.

Complementation Rule:
    We have and schema R and two sets of its columns (X, Y),
    with Z = R - X - Y:
        If X ->> Y then X ->> Z
    MVDs come in pairs: for X the values of Y are independent of the values of Z and vice versa

Example:
    R = {course_id, teacher_id, book}
    X = {course_id}, Y = {teacher_id}
    MVD: course_id ->> teacher_id
    Z = R - X - Y = {book}
    MVD course_id ->> book (by complementation)

    |-----------|------------|--------|
    | course_id | teacher_id | book   |
    |-----------|------------|--------|
    |     1     |   Tux      |  Linux |
    |     1     |   Tux      |  Java  |
    |     1     |   Duke     |  Linux |
    |     1     |   Duke     |  Java  |
    |-----------|------------|--------|

    Every teacher of a course appears with every book of that course (2 teachers x 2 books = 4 rows).
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
    def need_complementation_rule(table: Table) -> bool:
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
