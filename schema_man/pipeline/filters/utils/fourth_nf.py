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
    def is_in_bcnf(alerts: list[Alert]) -> bool:
        for a in alerts:
            if a.blocks_pipeline:
                return False
        return True

    @staticmethod
    def __are_there_any_mvd(table: Table) -> bool:
        if table.get_multivalued_dependencies():
            return True
        else:
            return False

    @staticmethod
    def __attribute_closure(determinant: tuple[str, ...],
                            table: Table) -> set[str]:
        """Return the closure X+ of determinant under the declared FDs.

        A determinant is a superkey when its closure contains every column
        of the table.
        """
        columns = {column.name for column in table.columns}
        closure = set(determinant)
        # The primary key determines every column by definition, even when
        # the user did not declare its FDs.
        if table.primary_key is not None and set(
            table.primary_key.columns
        ) <= closure:
            return columns
        # Apply every FD whose determinant is already inside the closure
        # until no new attribute can be added.
        changed = True
        while changed:
            changed = False
            for fd in table.get_functional_dependencies():
                if set(fd.determinant) <= closure:
                    new_attributes = set(fd.dependent) - closure
                    if new_attributes:
                        closure |= new_attributes
                        changed = True
        return closure

    @staticmethod
    def determinant_is_superkey(determinant: tuple[str, ...],
                                table: Table) -> bool:
        """Tell whether determinant is a superkey of the table."""
        columns = {column.name for column in table.columns}
        return FourthNormalFormDetecter.__attribute_closure(
            determinant, table
        ) == columns

    @staticmethod
    def __mvd_is_trivial(mvd: MultivaluedDependency,
                         columns: set[str]) -> bool:
        """An MVD X ->> Y is trivial if Y is a subset of X or X u Y = R."""
        determinant = set(mvd.determinant)
        dependent = set(mvd.dependent)
        return dependent <= determinant or determinant | dependent == columns

    @staticmethod
    def __decomposition_hint(mvd: MultivaluedDependency,
                             columns: set[str]) -> str:
        """Return the two relations proposed by the complementation rule.

        For a non-trivial MVD X ->> Y, with Z = R - X - Y:
            R1 = X u Y
            R2 = X u Z
        """
        determinant = set(mvd.determinant)
        dependent = set(mvd.dependent)
        rest = columns - determinant - dependent
        first = tuple(sorted(determinant | dependent))
        second = tuple(sorted(determinant | rest))
        return f"decompose into {first} and {second}"

    @staticmethod
    def detect_fourth_nf(table: Table):
        alerts: list[Alert] = []

        # No mvd declared (Gray alerts, can not detect)
        if not FourthNormalFormDetecter.__are_there_any_mvd(table):
            alerts.append(
                Alert(
                    AlertColor.GRAY,
                    "NO MVD IN THE TABLE",
                    table.name
                )
            )
            return alerts

        columns = {column.name for column in table.columns}

        """---------------
        Now the algorithm
        ---------------"""
        # 1. Extract the MVDs
        for mvd in table.get_multivalued_dependencies():
            # 2. A trivial MVD imposes no restriction, so it is not a
            # fourth normal form violation.
            if FourthNormalFormDetecter.__mvd_is_trivial(mvd, columns):
                continue
            # 3. For every non-trivial MVD X ->> Y, X must be a superkey.
            if FourthNormalFormDetecter.determinant_is_superkey(
                mvd.determinant, table
            ):
                alerts.append(
                    Alert(
                        AlertColor.GREEN,
                        f"{mvd.determinant} ->> {mvd.dependent} is implied "
                        "by a superkey",
                        table.name
                    )
                )
            # 4. Otherwise the table violates the fourth normal form; the
            # complementation rule suggests how to decompose it.
            else:
                hint = FourthNormalFormDetecter.__decomposition_hint(
                    mvd, columns
                )
                alerts.append(
                    Alert(
                        AlertColor.RED,
                        f"NON-TRIVIAL MVD {mvd.determinant} ->> "
                        f"{mvd.dependent} WITH NON-SUPERKEY DETERMINANT; "
                        f"{hint}",
                        table.name
                    )
                )

        # 5. Every MVD was trivial: the table satisfies the fourth normal form.
        if not alerts:
            alerts.append(
                Alert(
                    AlertColor.GREEN,
                    "NO NON-TRIVIAL MVD WITH A NON-SUPERKEY DETERMINANT",
                    table.name
                )
            )

        return alerts
