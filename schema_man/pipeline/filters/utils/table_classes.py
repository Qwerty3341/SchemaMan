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
