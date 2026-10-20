from pathlib import Path

import pytest

from schema_man.pipeline.context import PipeLineContext
from schema_man.pipeline.filters.parse_sql import ParseSqlFilter
from schema_man.pipeline.pipe import Pipe

SCHEMAS = [
    ("school.sql", "sqlite"),
    ("store.sql", "mysql"),
]


def load_schema(filename: str) -> str:
    schema_file = Path(__file__).parent / "schemas" / filename
    return schema_file.read_text(encoding="utf-8")


def parse_context(sql: str, dialect: str) -> PipeLineContext:
    context = PipeLineContext(
        sql=sql,
        dialect=dialect,
        target_normal_form="NF3",
    )
    return Pipe(filters=[ParseSqlFilter()]).run(context)


@pytest.mark.parametrize(("filename", "dialect"), SCHEMAS)
def test_valid_schema_passes_first_filter(filename, dialect):
    sql = load_schema(filename)

    context = parse_context(sql, dialect)

    assert context.sql == sql
    assert context.dialect == dialect


def test_empty_sql_is_rejected():
    with pytest.raises(ValueError, match="SQL must not be empty"):
        parse_context("   ", "sqlite")


def test_invalid_sql_reports_syntax_errors():
    with pytest.raises(ValueError, match="SQL with syntax errors"):
        parse_context("CREATE TABLE (", "sqlite")


def test_schema_rejected_with_wrong_dialect():
    # PRAGMA is SQLite-only; MySQL must reject school.sql
    with pytest.raises(ValueError, match="SQL with syntax errors"):
        parse_context(load_schema("school.sql"), "mysql")
