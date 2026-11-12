import re
from typing import override

from sqlglot import exp

from ..context import PipeLineContext
from ..filter import Filter
from .utils.data_types import generic_type_of
from .utils.table_classes import (
    Column,
    ForeignKey,
    FunctionalDependency,
    MultivaluedDependency,
    PrimaryKey,
    Table,
    UniqueKey,
)

"""
Regular expression for detect the FD and MVD

# Dependencies are declared as SQL comments: "-- FD: (a, b) -> (c)".
# "->>" is listed before "->" so the arrow of an MVD is not read as an FD.
"""
DEPENDENCY_PATTERN = re.compile(
    r"^\s*(FD|MVD):\s*\((?P<determinant>[^)]*)\)\s*(?P<arrow>->>|->)"
    r"\s*\((?P<dependent>[^)]*)\)\s*$"
)

# Classes for store FD and MVD
DEPENDENCY_CLASSES = {
    "->": FunctionalDependency,
    "->>": MultivaluedDependency,
}


class ModelSchemaFilter(Filter):
    @override
    def apply(self, context: PipeLineContext) -> PipeLineContext:
        """Model the SQL schema into generic table"""
        if context.sql_ast is None:
            raise ValueError("SQL must be parsed before modeling the schema")

        context.schema = self.model_schema(context.sql_ast, context.dialect)
        return context

    def model_schema(self, statements: list[exp.Expression], dialect: str) -> list[Table]:
        """
        Build one Table per CREATE TABLE
        skipping other statements (INSERTS, INDEX, ALTERS, ETC.)
        """

        tables = []
        for statement in statements:
            if (isinstance(statement, exp.Create)
                    and statement.args.get("kind") == "TABLE"):
                tables.append(self.table_to_generic_syntax(statement, dialect))
        return tables

    def table_to_generic_syntax(self, create: exp.Create, dialect: str) -> Table:
        schema = create.this  # exp.Schema with the columns and constraints
        table = Table(name=schema.this.name.upper())
        primary_key_columns: list[str] | None = None

        for node in schema.expressions:
            # Detect a column
            if isinstance(node, exp.ColumnDef):
                column, inline_primary_key = self.detect_column(node, dialect)
                table.columns.append(column)
                if inline_primary_key:
                    primary_key_columns = [column.name]
                if self.has_column_constraint(
                        node, exp.UniqueColumnConstraint):
                    table.unique_keys.append(
                        UniqueKey(columns=(column.name,))
                    )
            elif isinstance(node, exp.Constraint):  # Simple PK
                # Named constraints wrap the real node
                # CONSTRAINT fk_x FOREIGN KEY
                primary_key_columns = self.detect_constraints(
                    node.expressions, table, primary_key_columns
                )
            else:  # Composite PK
                primary_key_columns = self.detect_constraints(
                    [node], table, primary_key_columns
                )

        if primary_key_columns is not None:
            table.primary_key = PrimaryKey(columns=tuple(primary_key_columns))

        self.model_dependencies(table, schema.comments)
        return table

    def detect_constraints(self, nodes: list, table: Table, primary_key_columns: list[str] | None) -> list[str] | None:
        """
        Read PK/FK/UNIQUE constraints into the table, keeping any PK found
        """
        for node in nodes:
            if isinstance(node, exp.PrimaryKey):
                primary_key_columns = [
                    column.name.upper() for column in node.expressions
                ]
            elif isinstance(node, exp.UniqueColumnConstraint):
                table.unique_keys.append(self.detect_unique_key(node))
            elif isinstance(node, exp.ForeignKey):
                table.foreign_keys.append(self.detect_foreign_key(node))
        return primary_key_columns

    @staticmethod
    def has_column_constraint(
        column_def: exp.ColumnDef,
        constraint_type: type[exp.Expression],
    ) -> bool:
        """
        Report whether a column declares a constraint of the given type
        """
        return any(
            isinstance(constraint.kind, constraint_type)
            for constraint in column_def.constraints
        )

    def detect_column(self, column_def: exp.ColumnDef, dialect: str) -> tuple[Column, bool]:
        """
        Build a Column and report whether it declares an inline PK
        """

        inline_primary_key = self.has_column_constraint(
            column_def, exp.PrimaryKeyColumnConstraint
        )
        column = Column(
            name=column_def.name.upper(),
            type=generic_type_of(column_def.kind, dialect),
            size=self.detect_size(column_def.kind),
        )
        return column, inline_primary_key

    @staticmethod
    def detect_size(data_type: exp.DataType) -> tuple[int, ...]:
        """
        Return numeric type parameters (50,) or (10, 2).

        Parameters that are not numbers (ENUM values) no size.
        """
        size = []
        for parameter in data_type.expressions:
            if not parameter.name.isdigit():
                return ()
            size.append(int(parameter.name))
        return tuple(size)

    @staticmethod
    def detect_unique_key(unique: exp.UniqueColumnConstraint) -> UniqueKey:
        """
        Build a UniqueKey from a table-level UNIQUE constraint.

        SQLGlot stores the constrained columns in ``this`` (an exp.Schema);
        the optional index name is ignored, like PK/FK names are.
        """
        schema = unique.this
        columns = schema.expressions if isinstance(schema, exp.Schema) else []
        return UniqueKey(
            columns=tuple(column.name.upper() for column in columns)
        )

    @staticmethod
    def detect_foreign_key(foreign_key: exp.ForeignKey) -> ForeignKey:
        """
        Make the ForeignKey class instance for the table
        """
        reference = foreign_key.args["reference"].this  # exp.Schema
        return ForeignKey(
            columns=tuple(
                column.name.upper() for column in foreign_key.expressions
            ),
            referenced_table=reference.this.name.upper(),
            referenced_columns=tuple(
                column.name.upper() for column in reference.expressions
            ),
        )

    def model_dependencies(self, table: Table, comments: list[str] | None) -> None:
        """
        Read FD/MVD declarations from the tables SQL comments
        """

        for comment in comments or []:
            match = DEPENDENCY_PATTERN.match(comment)
            if match is None:
                continue
            dependency = DEPENDENCY_CLASSES[match["arrow"]](
                determinant=self._attributes(match["determinant"]),
                dependent=self._attributes(match["dependent"]),
            )
            if isinstance(dependency, FunctionalDependency):
                table.functional_dependencies.append(dependency)
            else:
                table.multivalued_dependencies.append(dependency)

    @staticmethod
    def _attributes(attribute_list: str) -> tuple[str, ...]:
        """
        Normalize a comma-separated attribute list into a tuple of names.
        """
        return tuple(
            name.strip().upper() for name in attribute_list.split(",")
        )
