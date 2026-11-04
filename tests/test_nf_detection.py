from pathlib import Path

import pytest

from schema_man.pipeline.context import PipeLineContext
from schema_man.pipeline.filters.model_schema import ModelSchemaFilter
from schema_man.pipeline.filters.nf_detection import NFDetectionFilter
from schema_man.pipeline.filters.parse_sql import ParseSqlFilter
from schema_man.pipeline.filters.utils.alerts import AlertColor
from schema_man.pipeline.pipe import Pipe

SIMPLE_PK_SQL = "CREATE TABLE materia (id INTEGER PRIMARY KEY, nombre TEXT);"
NO_PK_SQL = "CREATE TABLE sin_pk (nombre TEXT, otro TEXT);"
COMPOSITE_PK_SQL = """
CREATE TABLE inscripcion (
    alumno_id INTEGER NOT NULL,
    curso_id INTEGER NOT NULL,
    creditos INTEGER NOT NULL,
    PRIMARY KEY (alumno_id, curso_id)
);
"""


def load_school_sql() -> str:
    schema_file = Path(__file__).parent / "schemas" / "school.sql"
    return schema_file.read_text(encoding="utf-8")


def run_nf_detection(sql: str, target_normal_form: str, dialect: str = "sqlite"):
    context = PipeLineContext(
        sql=sql, dialect=dialect, target_normal_form=target_normal_form
    )
    pipeline = Pipe(
        filters=[ParseSqlFilter(), ModelSchemaFilter(), NFDetectionFilter()]
    )
    return pipeline.run(context)


def collected(context: PipeLineContext) -> list[tuple[AlertColor, str]]:
    return [(alert.color, alert.message) for alert in context.violations]


def test_unknown_normalization_level_is_rejected():
    with pytest.raises(ValueError, match="Unsupported normalization level"):
        run_nf_detection(SIMPLE_PK_SQL, "NF9")


def test_second_nf_is_not_evaluated_when_target_is_nf1():
    context = run_nf_detection(COMPOSITE_PK_SQL, "NF1")

    # The first normal form always runs...
    assert (AlertColor.GREEN, "NO REPEATING GROUPS FOUND") in collected(context)
    # ...but the second one is out of the requested target.
    assert not any(
        "FUNCTIONAL DEPENDENCIES" in message for _, message in collected(context)
    )


def test_second_nf_emits_green_for_simple_pk():
    context = run_nf_detection(SIMPLE_PK_SQL, "NF2")
    alerts = collected(context)

    assert (AlertColor.GREEN, "TABLE WITH SIMPLE PK") in alerts
    # A simple PK satisfies 2NF on its own, so the missing functional
    # dependencies are not a reason to stop the evaluation.
    assert not any(color == AlertColor.GRAY for color, _ in alerts)


def test_second_nf_emits_gray_without_declared_functional_dependencies():
    context = run_nf_detection(COMPOSITE_PK_SQL, "NF2")

    assert (
        AlertColor.GRAY,
        "TABLE DOES NOT HAVE FUNCTIONAL DEPENDENCIES",
    ) in collected(context)


def test_second_nf_is_not_evaluated_for_table_without_primary_key():
    context = run_nf_detection(NO_PK_SQL, "NF2")
    alerts = collected(context)

    assert (AlertColor.RED, "THIS TABLE DOES NOT HAVE A PRIMARY KEY") in alerts
    assert not any("SIMPLE PK" in message for _, message in alerts)
    assert not any(
        "FUNCTIONAL DEPENDENCIES" in message for _, message in alerts
    )


def test_second_nf_only_greys_tables_without_declared_functional_dependencies():
    context = run_nf_detection(load_school_sql(), "NF2")

    gray_tables = {
        alert.associated_table
        for alert in context.violations
        if alert.color == AlertColor.GRAY
    }
    # INSCRIPCION declares its FDs, so the gray branch is skipped for it.
    # CURSO_PROFESOR_LIBRO only declares an MVD, so there is no FD to check
    # the partial dependencies against.
    assert gray_tables == {"CURSO_PROFESOR_LIBRO"}
