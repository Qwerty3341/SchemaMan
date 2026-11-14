from pathlib import Path

from schema_man.pipeline.context import PipeLineContext
from schema_man.pipeline.filters.model_schema import ModelSchemaFilter
from schema_man.pipeline.filters.parse_sql import ParseSqlFilter
from schema_man.pipeline.filters.utils.data_types import GenericType
from schema_man.pipeline.pipe import Pipe


def load_store_sql() -> str:
    schema_file = Path(__file__).parent / "schemas" / "store.sql"
    return schema_file.read_text(encoding="utf-8")


def model_store_schema():
    context = PipeLineContext(
        sql=load_store_sql(),
        dialect="mysql",
        target_normal_form="NF3",
    )
    pipeline = Pipe(filters=[ParseSqlFilter(), ModelSchemaFilter()])
    return pipeline.run(context)


def test_store_schema_tables_and_generic_syntax(capsys):
    context = model_store_schema()
    schema = context.schema

    with capsys.disabled():  # Always show the generic schema in the terminal
        print("\n\n".join(table.to_generic() for table in schema))

    # CREATE DATABASE / USE are not tables and must be ignored
    assert [table.name for table in schema] == [
        "CLIENTE",
        "PEDIDO_DETALLE",
    ]

    cliente = schema[0]
    assert [(c.name, c.type, c.size) for c in cliente.columns] == [
        ("CLIENTE_ID", GenericType.INTEGER, ()),
        ("RFC", GenericType.STRING, (13,)),
        ("NOMBRE", GenericType.STRING, (100,)),
        ("CORREO", GenericType.STRING, (120,)),
    ]
    assert cliente.primary_key.columns == ("CLIENTE_ID",)
    assert [uk.columns for uk in cliente.unique_keys] == [("RFC",)]
    assert "UNIQUE: (RFC)" in cliente.to_generic()
    assert [
        (fd.determinant, fd.dependent) for fd in cliente.functional_dependencies
    ] == [
        (("CLIENTE_ID",), ("RFC", "NOMBRE", "CORREO")),
        (("RFC",), ("CLIENTE_ID", "NOMBRE", "CORREO")),
    ]
    assert cliente.foreign_keys == []
    assert cliente.multivalued_dependencies == []

    detalle = schema[1]
    assert [(c.name, c.type) for c in detalle.columns] == [
        ("PEDIDO_ID", GenericType.INTEGER),
        ("PRODUCTO_ID", GenericType.INTEGER),
        ("CLIENTE_ID", GenericType.INTEGER),
        ("NOMBRE_PRODUCTO", GenericType.STRING),
        ("PRECIO_UNITARIO", GenericType.DECIMAL),
        ("CATEGORIA_ID", GenericType.INTEGER),
        ("NOMBRE_CATEGORIA", GenericType.STRING),
        ("CANTIDAD", GenericType.INTEGER),
    ]
    # DECIMAL(10, 2) keeps both precision and scale
    assert detalle.columns[4].size == (10, 2)
    assert detalle.primary_key.columns == ("PEDIDO_ID", "PRODUCTO_ID")
    assert detalle.unique_keys == []
    # FOREIGN KEY declared with CONSTRAINT must still be detected
    assert [
        (fk.columns, fk.referenced_table, fk.referenced_columns)
        for fk in detalle.foreign_keys
    ] == [(("CLIENTE_ID",), "CLIENTE", ("CLIENTE_ID",))]
    assert [
        (fd.determinant, fd.dependent)
        for fd in detalle.functional_dependencies
    ] == [
        (("PEDIDO_ID", "PRODUCTO_ID"), ("CANTIDAD",)),
        (("PEDIDO_ID",), ("CLIENTE_ID",)),
        (
            ("PRODUCTO_ID",),
            ("NOMBRE_PRODUCTO", "PRECIO_UNITARIO", "CATEGORIA_ID"),
        ),
        (("CATEGORIA_ID",), ("NOMBRE_CATEGORIA",)),
    ]
    assert detalle.multivalued_dependencies == []


def test_unique_constraints_inline_and_composite():
    context = PipeLineContext(
        sql="""
            CREATE TABLE usuario (
                id INTEGER PRIMARY KEY,
                correo VARCHAR(120) UNIQUE,
                documento VARCHAR(20),
                pais VARCHAR(2),
                CONSTRAINT uq_documento_pais UNIQUE (documento, pais)
            );
        """,
        dialect="sqlite",
        target_normal_form="NF3",
    )
    pipeline = Pipe(filters=[ParseSqlFilter(), ModelSchemaFilter()])
    context = pipeline.run(context)
    table = context.schema[0]

    assert [uk.columns for uk in table.unique_keys] == [
        ("CORREO",),
        ("DOCUMENTO", "PAIS"),
    ]
    assert "UNIQUE: (CORREO)" in table.to_generic()
    assert "UNIQUE: (DOCUMENTO, PAIS)" in table.to_generic()


def test_join_dependency_comment_is_parsed():
    context = PipeLineContext(
        sql="""
            CREATE TABLE r (
                a INTEGER,
                b INTEGER,
                c INTEGER,
                PRIMARY KEY (a)
                -- FD: (a) -> (b, c)
                -- JD: (a, b), (b, c), (a, c)
            );
        """,
        dialect="sqlite",
        target_normal_form="NF5",
    )
    pipeline = Pipe(filters=[ParseSqlFilter(), ModelSchemaFilter()])
    context = pipeline.run(context)
    table = context.schema[0]

    assert [jd.components for jd in table.join_dependencies] == [
        (("A", "B"), ("B", "C"), ("A", "C")),
    ]
    assert [
        (fd.determinant, fd.dependent)
        for fd in table.functional_dependencies
    ] == [(("A",), ("B", "C"))]
    assert "JD: (A, B), (B, C), (A, C)" in table.to_generic()


def test_invalid_join_dependency_is_ignored():
    context = PipeLineContext(
        sql="""
            CREATE TABLE r (
                a INTEGER,
                b INTEGER,
                PRIMARY KEY (a)
                -- JD: (A, B)
            );
        """,
        dialect="sqlite",
        target_normal_form="NF5",
    )
    pipeline = Pipe(filters=[ParseSqlFilter(), ModelSchemaFilter()])
    context = pipeline.run(context)
    table = context.schema[0]

    # A JD needs at least two components.
    assert table.join_dependencies == []
