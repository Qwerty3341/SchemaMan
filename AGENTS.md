# SchemaMan

Flask app that parses a SQL schema and reports normal-form (1NF–5NF/BCNF)
compliance. Pipe-and-Filter backend with a thin JS front end.

## Commands

- Setup once: `python3 -m venv .venv`, activate it, then `python -m pip install -r requirements.txt`.
- Run: `flask --app schema_man run --debug` (from repo root).
- Tests: `pytest` (from repo root). `pytest.ini` sets `pythonpath = .`, so plain `pytest` works; no `python -m` needed.
- Single test: `pytest tests/test_get_report.py::test_valid_sql_returns_report`.
- Rebuild the editor bundle after editing `schema_man/static/js/codeEditor.js`:
  `npm ci` then `npx esbuild schema_man/static/js/codeEditor.js --bundle --outfile=schema_man/static/js/codeEditor.bundle.js`.
  The generated `codeEditor.bundle.js` is committed, so keep it in sync.
- No lint, typecheck, or CI is configured. `autopep8`/`pycodestyle` are installed but unconfigured.

## Architecture

- App factory `create_app()` in `schema_man/__init__.py` registers five blueprints: `main`/`manual`/`about` (`schema_man/schema_man.py`), `nf` (`schema_man/normal_forms.py`), and `api` (`schema_man/api.py`). Add routes to those modules or register a new blueprint in the factory. Optional gitignored config is `instance/config.py`; tests use `create_app({"TESTING": True})`.
- `Pipe` (`schema_man/pipeline/pipe.py`) threads one `PipeLineContext` through `Filter.apply(context)`. `GET /api/get_report` runs, in order: `ParseSqlFilter` → `ModelSchemaFilter` → `NFDetectionFilter` → `ReportFilter`; `POST /api/parse-sql` runs only `ParseSqlFilter`.
- Filters signal failure by raising `ValueError`; the API catches it and returns `400 {"valid": false, "error": ...}`. Do not build error responses inside filters.
- `PipeLineContext` (`pipeline/context.py`) carries inputs (`sql`, `dialect`, `target_normal_form`) and results (`sql_ast`, `schema`, `violations`, `report`, `report_tables`).
- Per-form detectors live in `pipeline/filters/utils/` (`first_nf.py` … `fifth.py`, `bcnf.py`) and are orchestrated by `pipeline/filters/nf_detection.py`. `NORMALIZATION_ORDER = ("NF1", "NF2", "NF3", "BCNF", "NF4", "NF5")` — BCNF sits between NF3 and NF4. Higher levels only run when the target reaches them, and a red alert stops evaluation for that table.

## Conventions an agent would otherwise miss

- API dialects are exactly `sqlite` and `mysql` (`mysql` also covers MariaDB); normalization levels are the `NORMALIZATION_ORDER` strings.
- FD/MVD/JD are not inferred from SQL. They are declared in SQL comments and parsed by regex in `model_schema.py`:
  - `-- FD: (a, b) -> (c)`
  - `-- MVD: (a, b) ->> (c)`
  - `-- JD: (a, b), (b, c), (a, c)`
- Alert colors: only `RED` fails a table (`[ FAILS ]` / `"status": "fails"`). `GREEN`/`YELLOW`/`GRAY` pass; `GRAY` means "indeterminate / missing info" and must not block higher-form evaluation.
- Modeling upper-cases all identifiers (`Table`, `Column`, keys); tests assert upper-case names.
- `docs/` covers the API, filters, report format, and algorithms, but is partially stale (e.g. `docs/ARCHITECTURE.md` mentions `sql_checked`). Treat the code as the source of truth.

## Tests

- `tests/` mirrors the pipeline; SQL fixtures live in `tests/schemas/` (`school.sql` = SQLite, `store.sql` = MySQL).
- API tests use the Flask test client via `create_app({"TESTING": True})`.
- `test_model_schema.py` and `test_store_schema.py` print the modeled schema to the terminal on every run (`capsys.disabled()`); that output is intentional.
