# SchemaMan

## Structure

- Flask app using the App Factory pattern; the entry point is `schema_man/__init__.py:create_app()`.
- Page routes are Blueprint modules in `schema_man/schema_man.py` and `schema_man/normal_forms.py`; templates and static assets are under `schema_man/templates/` and `schema_man/static/`.
- `instance/` is runtime-local and gitignored; default config is loaded from `instance/config.py` when present.
- `NormalForms.md` is the repository's domain reference for the 1NF–5NF rules.

## Commands

- Start the development server with `flask --app schema_man run` from the repository root.
- The checked-in `requirements.txt` is empty; the README's intended dependencies are Flask, sqlglot, pytest, and a future PDF library. Do not assume dependency installation is reproducible until that file is populated.
- There are currently no tests, linter, formatter, type checker, CI workflow, or code-generation step configured.

## Conventions

- Add web endpoints through the existing Blueprint structure and register new blueprints in `create_app()`.
- Use `create_app(test_config=...)` for test setup rather than constructing a Flask app directly.
