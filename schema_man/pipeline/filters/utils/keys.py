"""Candidate keys derived from primary keys, UNIQUE keys and FDs."""

from itertools import combinations

from .table_classes import Table


def _known_superkeys(table: Table) -> list[frozenset[str]]:
    """Return the superkeys declared by the schema (PK and UNIQUE)."""
    superkeys: list[frozenset[str]] = []

    primary_key = table.get_primary_key()
    if primary_key is not None:
        superkeys.append(frozenset(primary_key.columns))

    superkeys.extend(
        frozenset(unique.columns) for unique in table.get_unique_keys()
    )
    return superkeys


def _constraints(table: Table) -> list[tuple[set[str], set[str]]]:
    """Return the FDs plus K -> R for every declared superkey.

    The primary key and every UNIQUE key determine all the columns, so they
    are treated as functional dependencies of the form K -> R.
    """
    columns = {column.name for column in table.columns}
    constraints = [
        (set(fd.determinant), set(fd.dependent))
        for fd in table.get_functional_dependencies()
    ]
    constraints.extend(
        (set(superkey), set(columns)) for superkey in _known_superkeys(table)
    )
    return constraints


def _closure(
    attributes,
    constraints: list[tuple[set[str], set[str]]],
) -> set[str]:
    """Return the attribute closure under the given constraints."""
    closure = set(attributes)
    changed = True
    while changed:
        changed = False
        for determinant, dependent in constraints:
            if determinant <= closure:
                new_attributes = dependent - closure
                if new_attributes:
                    closure |= new_attributes
                    changed = True
    return closure


def attribute_closure(attributes, table: Table) -> set[str]:
    """Return the closure of attributes under the schema constraints."""
    return _closure(attributes, _constraints(table))


def is_superkey(attributes, table: Table) -> bool:
    """Tell whether attributes is a superkey of the table."""
    columns = {column.name for column in table.columns}
    if not columns:
        return False
    return _closure(attributes, _constraints(table)) >= columns


def candidate_keys(table: Table) -> set[frozenset[str]]:
    """Return every minimal set of attributes whose closure is the table.

    Subsets are explored in increasing size. The first superkey found in a
    branch is minimal, so all of its supersets can be pruned.
    """
    columns = {column.name for column in table.columns}
    if not columns:
        return set()

    constraints = _constraints(table)
    keys: list[frozenset[str]] = []
    ordered_columns = sorted(columns)

    for size in range(1, len(ordered_columns) + 1):
        for subset in combinations(ordered_columns, size):
            candidate = frozenset(subset)
            if any(key <= candidate for key in keys):
                continue
            if _closure(candidate, constraints) >= columns:
                keys.append(candidate)

    return set(keys)
