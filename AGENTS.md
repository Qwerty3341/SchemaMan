# SchemaMan

## App structure

- Flask app factory is `schema_man.create_app()` in `schema_man/__init__.py`; it registers blueprints `schema_man.schema_man` and `schema_man.normal_forms`.
- Templates and static assets live under `schema_man/templates/` and `schema_man/static/`. Add routes to existing blueprints and register any new blueprint in the factory.
- Optional local settings are loaded from gitignored `instance/config.py`; pass `test_config` to `create_app()` for test configuration.
- UI uses CodeMirror: `schema_man/templates/` loads `schema_man/static/js/codeEditor.bundle.js` (generated). This bundle must be built from `schema_man/static/js/codeEditor.js` via esbuild (see Setup).

## Setup

- Python deps: `python3 -m venv .venv`, activate it (`source .venv/bin/activate` on Linux/macOS), then `python -m pip install -r requirements.txt` (README has Windows equivalents).
- JS deps and bundle: install Node.js/npm, then run `npm ci` followed by `npx esbuild schema_man/static/js/codeEditor.js --bundle --outfile=schema_man/static/js/codeEditor.bundle.js`. Rebuild whenever `schema_man/static/js/codeEditor.js` changes.

## Commands

- Run (debug): `flask --app schema_man run --debug` (from repo root)
- Run (prod-like): `flask --app schema_man run` (from repo root)
- Tests: `pytest` (from repo root)

## Notes

- No lint, typecheck, or CI configuration is currently checked in.
- Architecture: Pipe and Filter (stated in README); primary libraries: `sqlglot`, `jinja`, `pytest`. Supported DB engines: SQLite, MariaDB.