from pathlib import Path

import pytest

from schema_man.pipeline.context import PipeLineContext
from schema_man.pipeline.filters.model_schema import ModelSchemaFilter
from schema_man.pipeline.filters.parse_sql import ParseSqlFilter
from schema_man.pipeline.filters.utils.alerts import AlertColor
from schema_man.pipeline.filters.utils.data_types import GenericType
from schema_man.pipeline.filters.utils.table_classes import Table
from schema_man.pipeline.pipe import Pipe


def load_school_sql() -> str:
    schema_file = Path(__file__).parent / "schemas" / "school.sql"
    return schema_file.read_text(encoding="utf-8")


def model_school_schema():
    context = PipeLineContext(
        sql=load_school_sql(),
        dialect="sqlite",
        target_normal_form="NF3",
    )
    pipeline = Pipe(filters=[ParseSqlFilter(), ModelSchemaFilter()])
    return pipeline.run(context)


def test_school_schema_tables_and_generic_syntax(capsys):
    context = model_school_schema()
    schema = context.schema

    assert context.sql_ast
    assert schema is not None
    assert all(isinstance(table, Table) for table in schema)

    with capsys.disabled():  # Always show the generic schema in the terminal
        print("\n\n".join(table.to_generic() for table in schema))

    assert [table.name for table in schema] == [
        "ALUMNO",
        "PROFESOR",
        "INSCRIPCION",
        "CURSO_PROFESOR_LIBRO",
    ]

    alumno = schema[0]
    assert [(c.name, c.type) for c in alumno.columns] == [
        ("ALUMNO_ID", GenericType.INTEGER),
        ("MATRICULA", GenericType.STRING),
        ("NOMBRE", GenericType.STRING),
        ("CORREO", GenericType.STRING),
    ]
    assert alumno.primary_key.columns == ("ALUMNO_ID",)
    assert [
        (fd.determinant, fd.dependent) for fd in alumno.functional_dependencies
    ] == [
        (("ALUMNO_ID",), ("MATRICULA", "NOMBRE", "CORREO")),
        (("MATRICULA",), ("ALUMNO_ID", "NOMBRE", "CORREO")),
    ]
    assert alumno.foreign_keys == []
    assert alumno.multivalued_dependencies == []

    profesor = schema[1]
    assert len(profesor.columns) == 7
    assert profesor.primary_key.columns == ("PROFESOR_ID",)
    assert [
        (fd.determinant, fd.dependent)
        for fd in profesor.functional_dependencies
    ] == [
        (("PROFESOR_ID",), ("NOMBRE", "DEPTO_ID")),
        (("DEPTO_ID",), ("NOMBRE_DEPTO",)),
    ]
    assert profesor.foreign_keys == []

    inscripcion = schema[2]
    assert inscripcion.primary_key.columns == ("ALUMNO_ID", "CURSO_ID")
    assert [
        (fk.columns, fk.referenced_table, fk.referenced_columns)
        for fk in inscripcion.foreign_keys
    ] == [(("ALUMNO_ID",), "ALUMNO", ("ALUMNO_ID",))]
    assert inscripcion.columns[4].type is GenericType.FLOAT
    assert [
        (fd.determinant, fd.dependent)
        for fd in inscripcion.functional_dependencies
    ] == [
        (("ALUMNO_ID", "CURSO_ID"), ("CALIFICACION",)),
        (("CURSO_ID",), ("NOMBRE_CURSO", "CREDITOS")),
    ]

    curso = schema[3]
    assert curso.primary_key.columns == ("CURSO_ID", "PROFESOR_ID", "LIBRO")
    assert [
        (fk.columns, fk.referenced_table, fk.referenced_columns)
        for fk in curso.foreign_keys
    ] == [(("PROFESOR_ID",), "PROFESOR", ("PROFESOR_ID",))]
    assert [
        (mvd.determinant, mvd.dependent)
        for mvd in curso.multivalued_dependencies
    ] == [(("CURSO_ID",), ("PROFESOR_ID",))]
    assert curso.functional_dependencies == []


def model_sql(sql: str) -> PipeLineContext:
    context = PipeLineContext(
        sql=sql,
        dialect="sqlite",
        target_normal_form="NF5",
    )
    pipeline = Pipe(filters=[ParseSqlFilter(), ModelSchemaFilter()])
    return pipeline.run(context)


def test_malformed_join_dependency_declaration_is_reported():
    context = model_sql("""
        CREATE TABLE r (
            a INTEGER,
            b INTEGER,
            c INTEGER,
            d INTEGER,
            PRIMARY KEY (a)
            -- JD: (a, b) (c, d)
        );
    """)

    assert [
        (alert.color, alert.associated_table, alert.message)
        for alert in context.violations
    ] == [(
        AlertColor.GRAY,
        "R",
        "MALFORMED JOIN DEPENDENCY DECLARATION: (a, b) (c, d)",
    )]


def test_malformed_functional_dependency_declaration_is_reported():
    context = model_sql("""
        CREATE TABLE r (
            a INTEGER,
            b INTEGER,
            c INTEGER,
            PRIMARY KEY (a)
            -- FD: (a) -> (b), (c)
        );
    """)

    assert [
        (alert.color, alert.message) for alert in context.violations
    ] == [(
        AlertColor.GRAY,
        "MALFORMED FUNCTIONAL DEPENDENCY DECLARATION: (a) -> (b), (c)",
    )]


def test_malformed_multivalued_dependency_declaration_is_reported():
    context = model_sql("""
        CREATE TABLE r (
            a INTEGER,
            b INTEGER,
            c INTEGER,
            PRIMARY KEY (a)
            -- MVD: (a) ->> (b), (c)
        );
    """)

    assert [
        (alert.color, alert.message) for alert in context.violations
    ] == [(
        AlertColor.GRAY,
        "MALFORMED MULTIVALUED DEPENDENCY DECLARATION: (a) ->> (b), (c)",
    )]


def test_plain_comments_are_not_reported():
    context = model_sql("""
        CREATE TABLE r (
            a INTEGER PRIMARY KEY,
            -- this table stores the available courses
            b INTEGER
        );
    """)

    assert context.violations == []


def test_valid_dependency_declarations_are_not_reported():
    context = model_sql("""
        CREATE TABLE r (
            a INTEGER,
            b INTEGER,
            c INTEGER,
            PRIMARY KEY (a)
            -- FD: (a) -> (b)
            -- MVD: (a) ->> (b)
            -- JD: (a, b), (b, c), (a, c)
        );
    """)

    assert context.violations == []


def test_model_schema_requires_parsed_ast():
    context = PipeLineContext(
        sql=load_school_sql(),
        dialect="sqlite",
        target_normal_form="NF3",
    )

    with pytest.raises(
        ValueError, match="SQL must be parsed before modeling the schema"
    ):
        ModelSchemaFilter().apply(context)
