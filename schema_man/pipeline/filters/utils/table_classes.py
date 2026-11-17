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
class UniqueKey:
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


@dataclass(frozen=True)
class JoinDependency:
    components: tuple[tuple[str, ...], ...]
    # Raw components as declared, kept only to report that the JD was
    # normalized. It does not take part in equality or hashing.
    original_components: tuple[tuple[str, ...], ...] | None = field(
        default=None, compare=False, repr=False
    )

    def __post_init__(self):
        original = (
            self.components
            if self.original_components is None
            else self.original_components
        )
        object.__setattr__(self, "original_components", original)

        # A join dependency is a set of sets: the order of the attributes
        # inside a component and repeated components do not matter.
        components: list[tuple[str, ...]] = []
        for component in self.components:
            attributes = tuple(sorted(set(component)))
            if attributes and attributes not in components:
                components.append(attributes)

        # A component contained in another one adds nothing to the join.
        minimal = tuple(
            component
            for component in components
            if not any(
                set(component) < set(other) for other in components
            )
        )
        object.__setattr__(self, "components", minimal)

    def label(self) -> str:
        """Render the normalized JD, flagging it when it was rewritten."""
        label = ", ".join(
            f"({', '.join(component)})" for component in self.components
        )
        if self.original_components != self.components:
            return f"{label} (NORMALIZED)"
        return label


@dataclass
class Table:
    name: str
    columns: list[Column] = field(default_factory=list)
    primary_key: PrimaryKey | None = None
    unique_keys: list[UniqueKey] = field(default_factory=list)
    foreign_keys: list[ForeignKey] = field(default_factory=list)
    functional_dependencies: list[FunctionalDependency] = field(
        default_factory=list)
    multivalued_dependencies: list[MultivaluedDependency] = field(
        default_factory=list)
    join_dependencies: list[JoinDependency] = field(default_factory=list)

    def get_name(self) -> str:
        return self.name

    def get_columns(self) -> tuple[Column, ...]:
        return tuple(self.columns)

    def get_primary_key(self) -> PrimaryKey | None:
        return self.primary_key

    def get_unique_keys(self) -> tuple[UniqueKey, ...]:
        return tuple(self.unique_keys)

    def get_foreign_keys(self) -> tuple[ForeignKey, ...]:
        return tuple(self.foreign_keys)

    def get_functional_dependencies(self) -> tuple[FunctionalDependency, ...]:
        return tuple(self.functional_dependencies)

    def get_multivalued_dependencies(self) -> tuple[MultivaluedDependency, ...]:
        return tuple(self.multivalued_dependencies)

    def get_join_dependencies(self) -> tuple[JoinDependency, ...]:
        return tuple(self.join_dependencies)

    def to_generic(self) -> str:
        """Render this table using the generic schema syntax."""
        lines = [f"TABLE {self.name}:"]

        for column in self.columns:
            size = f": {', '.join(map(str, column.size))}" if column.size else ""
            lines.append(f"    {column.name} {column.type}{size}")

        if self.primary_key is not None:
            columns = ", ".join(self.primary_key.columns)
            lines.append(f"    PRIMARY KEY: ({columns})")

        for unique_key in self.unique_keys:
            columns = ", ".join(unique_key.columns)
            lines.append(f"    UNIQUE: ({columns})")

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

        for join_dependency in self.join_dependencies:
            components = ", ".join(
                f"({', '.join(component)})"
                for component in join_dependency.components
            )
            lines.append(f"    JD: {components}")

        return "\n".join(lines)
