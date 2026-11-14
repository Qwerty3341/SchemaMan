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
