"""Fourth normal form

Requirements:
    1. The table must be in Boyce-Codd normal form.
    2. For every non-trivial multivalued dependency X ->> Y, X must be a superkey.

    An MVD X ->> Y is trivial if Y is a subset of X, or X v Y = R.

Complementation Rule:
    X = determinant
    Y = dependent
    Z = rest of the table

    We have and schema R and two sets of its columns (X, Y),
    with Z = R - X - Y:
        If X ->> Y then X ->> Z
    MVDs come in pairs: for X the values of Y are independent of the values of Z and vice versa

Example:
    R = {course, teacher, book}
    X = {course}, Y = {teacher}
    MVD: course ->> teacher
    Z = R - X - Y = {book}
    MVD course ->> book (by complementation)

    |-----------|------------|--------|
    | course    | teacher    | book   |
    |-----------|------------|--------|
    |     1     |   Tux      |  Linux |
    |     1     |   Tux      |  Java  |
    |     1     |   Duke     |  Linux |
    |     1     |   Duke     |  Java  |
    |-----------|------------|--------|

    Every teacher of a course appears with every book of that course (2 teachers x 2 books = 4 rows).

Solve:
    R1 = X u Y = {course, teacher}
    R2 = X u Z = {course, book}

    |-----------|------------|    |-----------|------------|
    | course    | teacher    |    | course    | book       |
    |-----------|------------|    |-----------|------------|
    |     1     |   Tux      |    |     1     |   Linux    |
    |     1     |   Duke     |    |     1     |   Java     |
    |-----------|------------|    |-----------|------------|
"""

from .alerts import Alert, AlertColor
from .table_classes import MultivaluedDependency, Table


class FourthNormalFormDetecter:
    @staticmethod
    def is_in_bcnf(alerts: list[Alert]):
        for a in alerts:
            if a.blocks_pipeline:
                return False
        return True

    @staticmethod
    def are_there_any_mvd(table: Table):
        if table.get_multivalued_dependencies():
            return True
        else:
            return False

    @staticmethod
    def mvd_need_complementation_rule(table: Table, mvd: MultivaluedDependency):
        """Return the missing complement MVD X ->> Z (Z = R - X - Y).

        Returns False when the complement is already declared or the MVD is
        trivial (no complementation needed).
        """
        # 1. Extract X and Y from mvd
        X = set(mvd.determinant)
        Y = set(mvd.dependent)
        # 2. Calculate Z (Z = R - X - Y), R is every column of the table
        R = {column.name for column in table.columns}
        Z = R - X - Y
        # 3. X u Y = R: trivial MVD, there is no complement to declare
        if not Z:
            return False
        # 4. Use the complementation rule to obtain C (C = X ->> Z)
        C = MultivaluedDependency(tuple(sorted(X)), tuple(sorted(Z)))
        # 5. Cycle to iterate in all the declared mvd
        for declared in table.get_multivalued_dependencies():
            # 5.1 Compare each declared mvd with C (as column sets,
            # the order inside determinant/dependent does not matter)
            if set(declared.determinant) == X and set(declared.dependent) == Z:
                # 5.2 The complementation is already in the table
                return False
        # 5.3 The cycle ended and there is no coincidence, return C
        return C

    @staticmethod
    def detect_fourth_nf(table: Table):
        alerts: list[Alert] = []

        # Simple key
        if table.primary_key is not None and len(table.primary_key.columns) == 1:
            alerts.append(
                Alert(
                    AlertColor.GREEN,
                    "SIMPLE PRIMARY KEY (PASSES 4NF)",
                    table.name
                )
            )
            return alerts

        # No mvd declared
        if not FourthNormalFormDetecter.are_there_any_mvd(table):
            alerts.append(
                Alert(
                    AlertColor.GRAY,
                    "NO MVD IN THE TABLE",
                    table.name
                )
            )
            return alerts

        # Check if the mvd needs complementation rule

        return alerts
