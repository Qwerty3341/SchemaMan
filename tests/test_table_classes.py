from schema_man.pipeline.filters.utils.data_types import GenericType
from schema_man.pipeline.filters.utils.table_classes import (
    Column,
    ForeignKey,
    FunctionalDependency,
    JoinDependency,
    MultivaluedDependency,
    PrimaryKey,
    Table,
    UniqueKey,
)


def test_table_getters_return_attributes_and_read_only_collections():
    column = Column(name="ID", type=GenericType.INTEGER)
    primary_key = PrimaryKey(columns=("ID",))
    unique_key = UniqueKey(columns=("NAME",))
    foreign_key = ForeignKey(
        columns=("ID",),
        referenced_table="OTHER",
        referenced_columns=("ID",),
    )
    functional_dependency = FunctionalDependency(
        determinant=("ID",), dependent=("NAME",)
    )
    multivalued_dependency = MultivaluedDependency(
        determinant=("ID",), dependent=("TAG",)
    )
    join_dependency = JoinDependency(
        components=(("ID", "NAME"), ("NAME", "TAG"), ("ID", "TAG"))
    )
    table = Table(
        name="EXAMPLE",
        columns=[column],
        primary_key=primary_key,
        unique_keys=[unique_key],
        foreign_keys=[foreign_key],
        functional_dependencies=[functional_dependency],
        multivalued_dependencies=[multivalued_dependency],
        join_dependencies=[join_dependency],
    )

    assert table.get_name() == "EXAMPLE"
    assert table.get_columns() == (column,)
    assert table.get_primary_key() == primary_key
    assert table.get_unique_keys() == (unique_key,)
    assert table.get_foreign_keys() == (foreign_key,)
    assert table.get_functional_dependencies() == (functional_dependency,)
    assert table.get_multivalued_dependencies() == (multivalued_dependency,)
    assert table.get_join_dependencies() == (join_dependency,)
    assert "JD: (ID, NAME), (NAME, TAG), (ID, TAG)" in table.to_generic()


def test_join_dependency_sorts_attributes_inside_each_component():
    join_dependency = JoinDependency(
        components=(("B", "A"), ("D", "C"))
    )

    assert join_dependency.components == (("A", "B"), ("C", "D"))


def test_join_dependency_removes_duplicate_components():
    join_dependency = JoinDependency(
        components=(("A", "B"), ("B", "A"), ("C",))
    )

    assert join_dependency.components == (("A", "B"), ("C",))


def test_join_dependency_removes_components_contained_in_another_one():
    join_dependency = JoinDependency(
        components=(("A", "B"), ("A",), ("C",))
    )

    assert join_dependency.components == (("A", "B"), ("C",))


def test_join_dependency_removes_repeated_attributes():
    join_dependency = JoinDependency(
        components=(("A", "A", "B"), ("C",))
    )

    assert join_dependency.components == (("A", "B"), ("C",))


def test_join_dependency_equality_uses_the_normalized_components():
    first = JoinDependency(components=(("A", "B"), ("C",)))
    second = JoinDependency(components=(("B", "A"), ("C",)))

    assert first == second


def test_join_dependency_label_flags_a_normalized_jd():
    join_dependency = JoinDependency(
        components=(("B", "A"), ("A",), ("C",))
    )

    assert join_dependency.label() == "(A, B), (C) (NORMALIZED)"


def test_join_dependency_label_does_not_flag_an_already_normalized_jd():
    join_dependency = JoinDependency(components=(("A", "B"), ("C",)))

    assert join_dependency.label() == "(A, B), (C)"


def test_join_dependency_rendering_uses_the_normalized_components():
    table = Table(
        name="EXAMPLE",
        columns=[
            Column(name="A", type=GenericType.INTEGER),
            Column(name="B", type=GenericType.INTEGER),
            Column(name="C", type=GenericType.INTEGER),
        ],
        join_dependencies=[
            JoinDependency(components=(("B", "A"), ("A",), ("C",)))
        ],
    )

    assert "JD: (A, B), (C)" in table.to_generic()
