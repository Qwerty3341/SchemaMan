from schema_man.pipeline.filters.utils.data_types import GenericType
from schema_man.pipeline.filters.utils.keys import (
    attribute_closure,
    candidate_keys,
    is_superkey,
)
from schema_man.pipeline.filters.utils.table_classes import (
    Column,
    FunctionalDependency,
    PrimaryKey,
    Table,
    UniqueKey,
)


def make_table(columns, primary_key=None, unique_keys=(), fds=()):
    return Table(
        name="R",
        columns=[
            Column(name=name, type=GenericType.INTEGER) for name in columns
        ],
        primary_key=(
            PrimaryKey(columns=tuple(primary_key)) if primary_key else None
        ),
        unique_keys=[UniqueKey(columns=tuple(uk)) for uk in unique_keys],
        functional_dependencies=[
            FunctionalDependency(determinant=tuple(d), dependent=tuple(dep))
            for d, dep in fds
        ],
    )


def test_simple_primary_key_is_the_only_candidate_key():
    table = make_table(["A", "B"], primary_key=["A"])
    assert candidate_keys(table) == {frozenset({"A"})}


def test_composite_primary_key_is_minimized():
    table = make_table(["A", "B", "C"], primary_key=["A", "B"])
    assert candidate_keys(table) == {frozenset({"A", "B"})}


def test_unique_keys_are_candidate_keys():
    table = make_table(["A", "B"], unique_keys=[["A"], ["B"]])
    assert candidate_keys(table) == {frozenset({"A"}), frozenset({"B"})}


def test_redundant_unique_key_is_removed():
    table = make_table(
        ["A", "B", "C"],
        primary_key=["A", "B"],
        unique_keys=[["A", "B", "C"]],
    )
    assert candidate_keys(table) == {frozenset({"A", "B"})}


def test_functional_dependency_derives_a_smaller_key():
    # A -> B makes A a key even though the declared PK is (A, B).
    table = make_table(
        ["A", "B"],
        primary_key=["A", "B"],
        fds=[(("A",), ("B",))],
    )
    assert candidate_keys(table) == {frozenset({"A"})}


def test_functional_dependency_derives_a_key_outside_the_primary_key():
    # C -> A and C -> B make C a key that is not part of the PK (A, B).
    table = make_table(
        ["A", "B", "C"],
        primary_key=["A", "B"],
        fds=[(("C",), ("A",)), (("C",), ("B",))],
    )
    assert candidate_keys(table) == {
        frozenset({"A", "B"}),
        frozenset({"C"}),
    }


def test_key_combining_a_functional_dependency_and_a_unique_key():
    # A -> C and UNIQUE (C, D) make (A, D) a candidate key.
    table = make_table(
        ["A", "B", "C", "D"],
        primary_key=["A", "B"],
        unique_keys=[["C", "D"]],
        fds=[(("A",), ("C",))],
    )
    assert candidate_keys(table) == {
        frozenset({"A", "B"}),
        frozenset({"A", "D"}),
        frozenset({"C", "D"}),
    }


def test_table_without_constraints_has_the_whole_table_as_key():
    # R is always a superkey; without smaller constraints it is the only key.
    table = make_table(["A", "B"])
    assert candidate_keys(table) == {frozenset({"A", "B"})}


def test_attribute_closure_and_is_superkey():
    table = make_table(
        ["A", "B", "C"],
        primary_key=["A"],
        fds=[(("B",), ("C",))],
    )
    assert attribute_closure({"B"}, table) == {"B", "C"}
    assert is_superkey({"A"}, table) is True
    assert is_superkey({"B"}, table) is False
