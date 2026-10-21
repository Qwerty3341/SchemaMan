# API

Blueprint for API (`schema_man/api.py`), mounted at `/api`.

## Context

Send the SQL to the Pipe and Filter backend. The endpoint builds a
`PipeLineContext` with the request data and executes a `Pipe` with a
`ParseSqlFilter`.

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

