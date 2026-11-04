# API

Blueprint for API (`schema_man/api.py`), mounted at `/api`.

## Context

Send the SQL to the Pipe and Filter backend. The endpoint builds a
`PipeLineContext` with the request data and executes a `Pipe` with a
`ParseSqlFilter`.

## Validation

`_validate_payload(data)` holds the checks shared by every endpoint. It
takes a plain dict (the JSON body for `POST`, the query string for `GET`)
and returns either the `(sql, dialect, normalization_level)` tuple or
`(None, (response, 400))`.

## Functions

### parse_sql

- route: `POST /api/parse-sql`
- data (JSON body):
  - `sql`: non-empty string
  - `dialect`: one of `sqlite`, `mysql` (There will be more dielects)
  - `normalization_level`: one of `NF1`, `NF2`, `NF3`, `BCNF`, `NF4`, `NF5`
- Creates a `PipeLineContext` (`normalization_level` → `target_normal_form`)
- Creates a `Pipe` with a `ParseSqlFilter` and calls `.run(context)`
- responses:
  - `200` => `{"valid": true}`
  - `400` => `{"valid": false, "error": "..."}` (validation error or `ValueError` from the pipeline)

### get_report

- route: `GET /api/get_report`
- data (query string, same fields as `parse_sql`):
  - `sql`: non-empty string
  - `dialect`: one of `sqlite`, `mysql`
  - `normalization_level`: one of `NF1`, `NF2`, `NF3`, `BCNF`, `NF4`, `NF5`
- Validates with `_validate_payload` reading `request.args`
- Creates a `PipeLineContext` and runs the whole pipeline:
  `ParseSqlFilter` → `ModelSchemaFilter` → `NFDetectionFilter` → `ReportFilter`
- responses:
  - `200` => `{"valid": true, "report": "...", "tables": [...]}`
    - `report`: plain text built by `ReportFilter` (`""` when the SQL has
      no `CREATE TABLE`)
    - `tables`: the same report as data, for the front-end to render with
      colors:

      ```json
      [{
        "name": "SIN_PK",
        "evaluated_level": "NF1",
        "status": "fails",
        "alerts": [
          {"color": "RED", "message": "THIS TABLE DOES NOT HAVE A PRIMARY KEY"},
          {"color": "GREEN", "message": "NO REPEATING GROUPS FOUND"}
        ]
      }]
      ```

      - `status`: `passes` | `fails` | `indeterminate`
        (`fails` when the table has a red alert, `indeterminate` when it has
        a gray alert, `passes` otherwise)
      - `alerts[].color`: `GREEN` | `YELLOW` | `RED` | `GRAY`
  - `400` => `{"valid": false, "error": "..."}` (validation error or `ValueError` from the pipeline)

