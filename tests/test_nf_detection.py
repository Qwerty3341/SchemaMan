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

    assert (AlertColor.GREEN, "TABLE WITH SIMPLE PK (PASS 2NF)") in alerts
    # A simple PK satisfies 2NF on its own, so the missing functional
    # dependencies are not a reason to stop the evaluation.
    assert not any(color == AlertColor.GRAY for color, _ in alerts)


def test_second_nf_reports_the_partial_dependency_of_inscripcion():
    context = run_nf_detection(load_school_sql(), "NF2")

    # CURSO_ID alone determines NOMBRE_CURSO and CREDITOS, so only part of
    # the composite key is used. The FD on the whole key is not reported.
    assert [
        (alert.color, alert.associated_table, alert.message)
        for alert in context.violations
        if "PARTIAL DEPENDENCY" in alert.message
    ] == [(
        AlertColor.RED,
        "INSCRIPCION",
        "PARTIAL DEPENDENCY: (CURSO_ID) -> (NOMBRE_CURSO, CREDITOS)",
    )]


def test_second_nf_passes_when_the_only_fd_uses_the_whole_key():
    sql = """
    CREATE TABLE ejemplo (
        a INTEGER,
        b INTEGER,
        c TEXT,
        PRIMARY KEY (a, b)
        -- FD: (a, b) -> (c)
    );
    """
    context = run_nf_detection(sql, "NF2")
    alerts = collected(context)

    assert (AlertColor.GREEN, "NO PARTIAL DEPENDENCIES (PASS 2NF)") in alerts
    assert not any(color == AlertColor.RED for color, _ in alerts)


def test_second_nf_ignores_fds_whose_determinant_is_not_part_of_the_pk():
    sql = """
    CREATE TABLE detalle (
        a INTEGER,
        b INTEGER,
        c INTEGER,
        d TEXT,
        PRIMARY KEY (a, b)
        -- FD: (a, b) -> (c)
        -- FD: (c) -> (d)
    );
    """
    context = run_nf_detection(sql, "NF2")
    alerts = collected(context)

    # (C) -> (D) is a transitive dependency (third normal form business),
    # not a partial one, so it must not fail here.
    assert (AlertColor.GREEN, "NO PARTIAL DEPENDENCIES (PASS 2NF)") in alerts
    assert not any(color == AlertColor.RED for color, _ in alerts)


def test_second_nf_ignores_fds_between_prime_attributes():
    sql = """
    CREATE TABLE claves (
        a INTEGER,
        b INTEGER,
        c TEXT,
        PRIMARY KEY (a, b)
        -- FD: (a, b) -> (c)
        -- FD: (b) -> (a)
    );
    """
    context = run_nf_detection(sql, "NF2")
    alerts = collected(context)

    # A depends on part of the key but A is prime, so 2NF is not violated.
    assert (AlertColor.GREEN, "NO PARTIAL DEPENDENCIES (PASS 2NF)") in alerts
    assert not any(color == AlertColor.RED for color, _ in alerts)


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


def test_only_red_blocks_the_pipeline():
    assert AlertColor.RED.blocks_pipeline is True
    assert AlertColor.GREEN.blocks_pipeline is False
    assert AlertColor.YELLOW.blocks_pipeline is False
    assert AlertColor.GRAY.blocks_pipeline is False


def test_third_nf_emits_gray_without_declared_functional_dependencies():
    context = run_nf_detection(COMPOSITE_PK_SQL, "NF3")
    alerts = collected(context)

    assert (
        AlertColor.GRAY,
        "CANNOT CHECK TRANSITIVE DEPENDENCIES WITHOUT FUNCTIONAL "
        "DEPENDENCIES",
    ) in alerts
    # Gray no longer stops the flow, but it must not turn into a fake pass.
    assert not any(
        color == AlertColor.GREEN and "TRANSITIVE DEPENDENCIES" in message
        for color, message in alerts
    )


def test_bcnf_emits_gray_without_declared_functional_dependencies():
    context = run_nf_detection(COMPOSITE_PK_SQL, "BCNF")

    assert (
        AlertColor.GRAY,
        "CANNOT CHECK CANDIDATE KEYS WITHOUT FUNCTIONAL DEPENDENCIES",
    ) in collected(context)


def test_gray_does_not_stop_the_pipeline():
    context = run_nf_detection(COMPOSITE_PK_SQL, "NF4")
    alerts = collected(context)

    # 2NF, 3NF, BCNF and 4NF report the missing information and the
    # evaluation keeps going.
    assert (
        AlertColor.GRAY,
        "TABLE DOES NOT HAVE FUNCTIONAL DEPENDENCIES",
    ) in alerts
    assert (
        AlertColor.GRAY,
        "CANNOT CHECK TRANSITIVE DEPENDENCIES WITHOUT FUNCTIONAL "
        "DEPENDENCIES",
    ) in alerts
    assert (
        AlertColor.GRAY,
        "CANNOT CHECK CANDIDATE KEYS WITHOUT FUNCTIONAL DEPENDENCIES",
    ) in alerts
    assert (AlertColor.GRAY, "NO MVD IN THE TABLE") in alerts
    assert not any(color == AlertColor.RED for color, _ in alerts)


def test_bcnf_is_not_evaluated_when_third_nf_fails():
    sql = """
    CREATE TABLE ejemplo (
        a INTEGER PRIMARY KEY,
        b INTEGER,
        c TEXT
        -- FD: (a) -> (b)
        -- FD: (b) -> (c)
    );
    """
    context = run_nf_detection(sql, "BCNF")
    alerts = collected(context)

    # (b) -> (c) is a transitive dependency: third normal form fails.
    assert any(
        color == AlertColor.RED and "TRANSITIVE DEPENDENCY" in message
        for color, message in alerts
    )
    # BCNF would flag the same dependency again, but the third normal form
    # gate stops it.
    assert not any("candidat key" in message for _, message in alerts)


def test_bcnf_runs_when_third_nf_passes():
    sql = """
    CREATE TABLE ejemplo (
        a INTEGER,
        b INTEGER,
        c TEXT,
        PRIMARY KEY (a, b)
        -- FD: (a, b) -> (c)
    );
    """
    context = run_nf_detection(sql, "BCNF")
    alerts = collected(context)

    assert (AlertColor.GREEN, "NO TRANSITIVE DEPENDENCIES FOUND") in alerts
    assert any(
        color == AlertColor.GREEN and "is candidate key" in message
        for color, message in alerts
    )


def test_fourth_nf_flags_nontrivial_mvd_without_superkey():
    context = run_nf_detection(load_school_sql(), "NF4")

    assert any(
        alert.color == AlertColor.RED
        and alert.associated_table == "CURSO_PROFESOR_LIBRO"
        and "CURSO_ID" in alert.message
        and "PROFESOR_ID" in alert.message
        for alert in context.violations
    )


def test_fourth_nf_flags_nontrivial_mvd_with_simple_primary_key():
    sql = """
    CREATE TABLE ejemplo (
        id INTEGER PRIMARY KEY,
        a INTEGER,
        b INTEGER
        -- MVD: (a) ->> (b)
    );
    """
    context = run_nf_detection(sql, "NF4")

    # A simple primary key does not make a non-trivial MVD with a
    # non-superkey determinant valid.
    assert any(
        alert.color == AlertColor.RED
        and "NON-TRIVIAL MVD" in alert.message
        for alert in context.violations
    )


def test_fourth_nf_passes_mvd_whose_determinant_is_a_superkey():
    sql = """
    CREATE TABLE ejemplo (
        id INTEGER PRIMARY KEY,
        a INTEGER,
        b INTEGER
        -- MVD: (id) ->> (a)
    );
    """
    context = run_nf_detection(sql, "NF4")
    alerts = collected(context)

    assert any(
        color == AlertColor.GREEN and "is implied by a superkey" in message
        for color, message in alerts
    )
    assert not any(color == AlertColor.RED for color, _ in alerts)


def test_fourth_nf_ignores_trivial_mvds():
    sql = """
    CREATE TABLE union_trivial (
        a INTEGER,
        b INTEGER,
        c INTEGER,
        PRIMARY KEY (a, b)
        -- MVD: (a, b) ->> (c)
    );
    CREATE TABLE subset_trivial (
        a INTEGER,
        b INTEGER,
        c INTEGER,
        PRIMARY KEY (a, b)
        -- MVD: (a, b) ->> (a)
    );
    """
    context = run_nf_detection(sql, "NF4")
    alerts = collected(context)

    # X u Y = R and Y subset of X: both MVDs are trivial, no violation.
    assert not any(color == AlertColor.RED for color, _ in alerts)
    assert (
        AlertColor.GREEN,
        "NO NON-TRIVIAL MVD WITH A NON-SUPERKEY DETERMINANT",
    ) in alerts
