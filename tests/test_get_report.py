import pytest

from schema_man import create_app

VALID_SQL = "CREATE TABLE materia (id INTEGER PRIMARY KEY, nombre TEXT);"
SQL_WITHOUT_PK = "CREATE TABLE sin_pk (nombre TEXT);"
SQL_COMPOSITE_PK_WITHOUT_FDS = """
CREATE TABLE inscripcion (
    alumno_id INTEGER NOT NULL,
    curso_id INTEGER NOT NULL,
    creditos INTEGER NOT NULL,
    PRIMARY KEY (alumno_id, curso_id)
);
"""


@pytest.fixture()
def client():
    app = create_app({"TESTING": True})
    return app.test_client()


def get_report(client, **params):
    return client.get("/api/get_report", query_string=params)


def test_valid_sql_returns_report(client):
    response = get_report(
        client,
        sql=VALID_SQL,
        dialect="sqlite",
        normalization_level="NF1",
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["valid"] is True
    assert "Table: MATERIA" in data["report"]
    assert "Evaluated level: NF1" in data["report"]
    assert "[ PASSES ]" in data["report"]


def test_table_without_primary_key_fails(client):
    response = get_report(
        client,
        sql=SQL_WITHOUT_PK,
        dialect="sqlite",
        normalization_level="NF1",
    )

    assert response.status_code == 200
    report = response.get_json()["report"]
    assert "[ FAILS ]" in report
    assert "THIS TABLE DOES NOT HAVE A PRIMARY KEY" in report


def test_sql_without_tables_returns_empty_report(client):
    response = get_report(
        client,
        sql="SELECT 1;",
        dialect="sqlite",
        normalization_level="NF1",
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["valid"] is True
    assert data["report"] == ""
    assert data["tables"] == []


def test_report_tables_carry_the_alert_colors(client):
    response = get_report(
        client,
        sql=SQL_WITHOUT_PK,
        dialect="sqlite",
        normalization_level="NF1",
    )

    assert response.status_code == 200
    tables = response.get_json()["tables"]
    assert len(tables) == 1

    table = tables[0]
    assert table["name"] == "SIN_PK"
    assert table["evaluated_level"] == "NF1"
    assert table["status"] == "fails"
    assert {
        "color": "RED",
        "message": "THIS TABLE DOES NOT HAVE A PRIMARY KEY",
    } in table["alerts"]
    assert all(
        alert["color"] in {"GREEN", "YELLOW", "RED", "GRAY"}
        for alert in table["alerts"]
    )


def test_report_tables_passing_table(client):
    response = get_report(
        client,
        sql=VALID_SQL,
        dialect="sqlite",
        normalization_level="NF1",
    )

    assert response.status_code == 200
    tables = response.get_json()["tables"]
    assert len(tables) == 1
    assert tables[0]["name"] == "MATERIA"
    assert tables[0]["status"] == "passes"
    assert tables[0]["alerts"]


def test_report_tables_with_gray_alert_pass(client):
    response = get_report(
        client,
        sql=SQL_COMPOSITE_PK_WITHOUT_FDS,
        dialect="sqlite",
        normalization_level="NF2",
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "[ PASSES ]" in data["report"]
    assert "[ INDETERMINATE ]" not in data["report"]

    tables = data["tables"]
    assert len(tables) == 1
    assert tables[0]["name"] == "INSCRIPCION"
    assert tables[0]["status"] == "passes"
    assert {
        "color": "GRAY",
        "message": "TABLE DOES NOT HAVE FUNCTIONAL DEPENDENCIES",
    } in tables[0]["alerts"]


def test_missing_sql_is_rejected(client):
    response = get_report(client, dialect="sqlite", normalization_level="NF1")

    assert response.status_code == 400
    assert response.get_json()["error"] == "SQL must be a non-empty text"


def test_missing_normalization_level_is_rejected(client):
    response = get_report(client, sql=VALID_SQL, dialect="sqlite")

    assert response.status_code == 400
    assert (
        response.get_json()["error"]
        == "Normalization level is required and must be text"
    )


def test_unsupported_dialect_is_rejected(client):
    response = get_report(
        client,
        sql=VALID_SQL,
        dialect="postgres",
        normalization_level="NF1",
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Unsupported dialect: postgres"


def test_unsupported_normalization_level_is_rejected(client):
    response = get_report(
        client,
        sql=VALID_SQL,
        dialect="sqlite",
        normalization_level="NF9",
    )

    assert response.status_code == 400
    assert (
        response.get_json()["error"]
        == "Unsupported normalization level: NF9"
    )


def test_invalid_sql_reports_syntax_errors(client):
    response = get_report(
        client,
        sql="CREATE TABLE (",
        dialect="sqlite",
        normalization_level="NF1",
    )

    assert response.status_code == 400
    assert "SQL with syntax errors" in response.get_json()["error"]
