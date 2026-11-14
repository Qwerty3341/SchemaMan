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
        3.1. Extract the JDs
        3.2. If no JD is declared
            3.2.1. Put a gray alert (NO JOIN DEPENDENCIES DECLARED):
                   without a declared JD the compliance cannot be proven
        3.3. For each JD
            3.3.1. If the union of the components is not the whole table put a
                   gray alert (the JD is malformed) and continue
            3.3.2. If one component contains all the columns the JD is
                   trivial: put a green alert
            3.3.3. Merge the components: if two components share columns and
                   that intersection is a superkey, put them together in one
                   component. Repeat until nothing can be merged
            3.3.4. If a component reaches all the columns put a green alert
                   (the JD is implied by the keys)
            3.3.5. Otherwise put a red alert
                   (JOIN DEPENDENCY NOT IMPLIED BY THE KEYS)
"""

from .alerts import Alert, AlertColor
from .fourth_nf import FourthNormalFormDetecter
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
    def check_if_each_jd_are_implied_by_keys(table: Table) -> list[Alert]:
        alerts: list[Alert] = []
        columns = {column.name for column in table.columns}

        join_dependencies = table.get_join_dependencies()
        if not join_dependencies:
            alerts.append(
                Alert(
                    AlertColor.GRAY,
                    "NO JOIN DEPENDENCIES DECLARED",
                    table.name
                )
            )
            return alerts

        for join_dependency in join_dependencies:
            components = [
                set(component) for component in join_dependency.components
            ]
            label = ", ".join(
                f"({', '.join(component)})"
                for component in join_dependency.components
            )

            # 3.3.1. The JD must cover every column of the table.
            if set().union(*components) != columns:
                alerts.append(
                    Alert(
                        AlertColor.GRAY,
                        f"JOIN DEPENDENCY {label} DOES NOT COVER EVERY COLUMN",
                        table.name
                    )
                )
                continue

            # 3.3.2. A component equal to the whole table makes the JD
            # trivial, so it imposes no restriction.
            if any(component == columns for component in components):
                alerts.append(
                    Alert(
                        AlertColor.GREEN,
                        f"TRIVIAL JOIN DEPENDENCY {label}",
                        table.name
                    )
                )
                continue

            # 3.3.3. Merge components whose intersection is a superkey.
            merged = True
            while merged:
                merged = False
                for i in range(len(components)):
                    for j in range(i + 1, len(components)):
                        intersection = components[i] & components[j]
                        if not intersection:
                            continue
                        if not FourthNormalFormDetecter.determinant_is_superkey(
                            tuple(intersection), table
                        ):
                            continue
                        components[i] |= components[j]
                        del components[j]
                        merged = True
                        break
                    if merged:
                        break

            # 3.3.4. / 3.3.5. The JD is implied by the keys when the merge
            # process reduces it to the whole table.
            if any(component == columns for component in components):
                alerts.append(
                    Alert(
                        AlertColor.GREEN,
                        f"JOIN DEPENDENCY {label} IS IMPLIED BY THE KEYS",
                        table.name
                    )
                )
            else:
                alerts.append(
                    Alert(
                        AlertColor.RED,
                        f"JOIN DEPENDENCY {label} IS NOT IMPLIED BY THE KEYS",
                        table.name
                    )
                )

        return alerts

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

        return FifthNormalFormDetecter.check_if_each_jd_are_implied_by_keys(
            table
        )
