"""
First normal form algorithm detecter

Requirements
    1. The table must have a primary key.
    2. The table must not contain repeating groups.
    3. The table must not contain matrix fields.
"""

from collections import defaultdict
from itertools import combinations
import re

from .alerts import Alert, AlertColor
from .data_types import GenericType
from .table_classes import Table


class FirstNormalFormDetecter:
    @staticmethod
    def detect_primary_key(table: Table) -> Alert:
        """Type of alert: green or red"""
        primary_key = table.get_primary_key()

        # Don't have pk
        if primary_key is None:
            return Alert(
                AlertColor.RED,
                "THIS TABLE DOES NOT HAVE A PRIMARY KEY",
                table.name,
            )

        # Have the pk
        return Alert(AlertColor.GREEN, "TABLE WITH PRIMARY KEY", table.name)

    @staticmethod
    def detect_repeating_groups(table: Table) -> list[Alert]:
        """Type of alert: green, yellow or red"""
        list_of_alerts: list[Alert] = []

        # Regex documented in NORMAL_FORMS_ALGORITHMS.md
        RG_REGEX = re.compile(r"^(?P<base>.+?)_?(?P<num>\d+)$")
        groups = defaultdict(list)

        # Detect repeating groups
        for column in table.columns:
            match = RG_REGEX.match(column.name)
            if match:  # if the current column matchs with RG_REGEX append it to the dict
                base = match.group("base").lower()
                groups[base].append(column.name)

        grouped_columns = set()

        # Put the alerts
        for base, columns in groups.items():
            if len(columns) >= 3:  # RED Alert 3 or more columns
                list_of_alerts.append(Alert(
                    AlertColor.RED,
                    f"REPEATING GROUP '{base}' : '{', '.join(columns)}'",
                    table.name,
                ))
                grouped_columns.update(columns)
            elif len(columns) == 2:  # Yellow, suspicion of repeatead groups
                list_of_alerts.append(Alert(
                    AlertColor.YELLOW,
                    f"POSSIBLE REPEATING GROUP '{base}' : '{', '.join(columns)}",
                    table.name,
                ))
                grouped_columns.update(columns)

        # Columns with a similarity in name
        remaining_columns = [
            c.name for c in table.columns if c.name not in grouped_columns]
        for name_a, name_b in combinations(remaining_columns, 2):
            n_a, n_b = name_a.lower(), name_b.lower()
            if n_a in n_b or n_b in n_a:
                list_of_alerts.append(Alert(
                    AlertColor.YELLOW,
                    f"SIMILAR COLUMN NAMES: {name_a}, {name_b}",
                    table.name,
                ))

        # At this point the alerts will be RED or Yellow
        if list_of_alerts:
            return list_of_alerts

        # If no alerts it means a GREEN Alert
        list_of_alerts.append(Alert(
            AlertColor.GREEN,
            "NO REPEATING GROUPS FOUND",
            table.name,
        ))
        return list_of_alerts

    @staticmethod
    def detect_matrix_fields(table: Table) -> list[Alert]:
        """Type of alert: yellow"""
        list_of_alerts = []

        for colum in table.columns:
            colum_lenght = max(colum.size, default=0)
            if colum.type == GenericType.STRING and colum_lenght >= 100:
                list_of_alerts.append(Alert(
                    AlertColor.YELLOW,
                    f"POSSIBLE MATRIX FIELD: {colum.name}: {colum_lenght} chars",
                    table.name
                ))

                # At this point the alerts will be Yellow
        if list_of_alerts:
            return list_of_alerts

        # If no alerts it means a GREEN Alert
        list_of_alerts.append(Alert(
            AlertColor.GREEN,
            "NO MATRIX FIELDS FOUND",
            table.name,
        ))

        return list_of_alerts

    @staticmethod
    def detect_first_nf(table: Table) -> list[Alert]:
        alerts = [FirstNormalFormDetecter.detect_primary_key(table)]
        alerts.extend(FirstNormalFormDetecter.detect_repeating_groups(table))
        alerts.extend(FirstNormalFormDetecter.detect_matrix_fields(table))
        return alerts
