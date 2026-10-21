from dataclasses import dataclass, field

from .data_types import GenericType


@dataclass(frozen=True)
class Column:
    name: str
    type: GenericType
    size: tuple[int, ...] = ()


@dataclass(frozen=True)
class PrimaryKey:
    columns: tuple[str, ...]


@dataclass(frozen=True)
class ForeignKey:
    columns: tuple[str, ...]
    referenced_table: str
    referenced_columns: tuple[str, ...]


@dataclass(frozen=True)
class Dependency:
    determinant: tuple[str, ...]
    dependent: tuple[str, ...]


@dataclass(frozen=True)
class FunctionalDependency(Dependency):
    pass


@dataclass(frozen=True)
class MultivaluedDependency(Dependency):
    pass


@dataclass
class Table:
    name: str
    columns: list[Column] = field(default_factory=list)
    primary_key: PrimaryKey | None = None
    foreign_keys: list[ForeignKey] = field(default_factory=list)
    functional_dependencies: list[FunctionalDependency] = field(
        default_factory=list)
    multivalued_dependencies: list[MultivaluedDependency] = field(
        default_factory=list)

    def to_generic(self) -> str:
        """Render this table using the generic schema syntax."""
        lines = [f"TABLE {self.name}:"]

        for column in self.columns:
            size = f": {', '.join(map(str, column.size))}" if column.size else ""
            lines.append(f"    {column.name} {column.type}{size}")

        if self.primary_key is not None:
            columns = ", ".join(self.primary_key.columns)
            lines.append(f"    PRIMARY KEY: ({columns})")

        for foreign_key in self.foreign_keys:
            columns = ", ".join(foreign_key.columns)
            referenced = ", ".join(foreign_key.referenced_columns)
            lines.append(
                f"    FOREIGN KEY: ({columns}) -> "
                f"{foreign_key.referenced_table}({referenced})")

        for dependency in self.functional_dependencies:
            determinant = ", ".join(dependency.determinant)
            dependent = ", ".join(dependency.dependent)
            lines.append(f"    FD: ({determinant}) -> ({dependent})")

        for dependency in self.multivalued_dependencies:
            determinant = ", ".join(dependency.determinant)
            dependent = ", ".join(dependency.dependent)
            lines.append(f"    MVD: ({determinant}) ->> ({dependent})")

        return "\n".join(lines)
