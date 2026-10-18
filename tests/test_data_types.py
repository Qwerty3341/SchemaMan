import pytest
import sqlglot
from sqlglot import exp

from schema_man.pipeline.filters.utils.data_types import (
    GenericType,
    generic_type_of,
)


@pytest.mark.parametrize(
    ("engine", "sql_type", "expected"),
    [
        ("sqlite", "INTEGER", GenericType.INTEGER),
        ("sqlite", "VARCHAR(50)", GenericType.STRING),
        ("sqlite", "TEXT", GenericType.STRING),
        ("sqlite", "BLOB", GenericType.BINARY),
        ("sqlite", "REAL", GenericType.FLOAT),
        ("sqlite", "NUMERIC", GenericType.DECIMAL),
        ("sqlite", "FOOBAR", GenericType.DECIMAL),
        ("mysql", "TINYINT", GenericType.INTEGER),
        ("mysql", "INT", GenericType.INTEGER),
        ("mysql", "BIGINT", GenericType.INTEGER),
        ("mysql", "CHAR(5)", GenericType.STRING),
        ("mysql", "DECIMAL(10, 2)", GenericType.DECIMAL),
        ("mysql", "TIMESTAMP", GenericType.DATETIME),
        ("mysql", "ENUM('a', 'b')", GenericType.ENUM),
        ("mysql", "JSON", GenericType.JSON),
    ],
)
def test_generic_type_of(engine, sql_type, expected):
    statement = sqlglot.parse_one(
        f"CREATE TABLE test (value {sql_type})",
        dialect=engine,
    )
    data_type = statement.find(exp.ColumnDef).kind

    assert generic_type_of(data_type, engine) is expected


def test_unmapped_type_returns_unknown():
    data_type = exp.DataType(this=exp.DataType.Type.USERDEFINED)

    assert generic_type_of(data_type, "mysql") is GenericType.UNKNOWN


def test_engine_names_are_case_insensitive():
    data_type = exp.DataType(this=exp.DataType.Type.INT)

    assert generic_type_of(data_type, "MySQL") is GenericType.INTEGER


def test_unsupported_engine_raises_value_error():
    data_type = exp.DataType(this=exp.DataType.Type.INT)

    with pytest.raises(ValueError, match="Unsupported engine"):
        generic_type_of(data_type, "mariadb")
