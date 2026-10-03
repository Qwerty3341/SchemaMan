# SchemaMan

## App structure

- Flask app factory is `schema_man.create_app()` in `schema_man/__init__.py`; it registers page blueprints from `schema_man/schema_man.py` and `schema_man/normal_forms.py`.
- Templates and static assets live under `schema_man/templates/` and `schema_man/static/`. Add routes to the existing blueprints and register any new blueprint in the factory.
- Optional local settings are loaded from gitignored `instance/config.py`; pass `test_config` to `create_app()` for test configuration.

## Commands

- Set up dependencies with `python3 -m venv .venv`, activate it, then `python -m pip install -r requirements.txt` (README has Windows equivalents).
- Run the app from the repository root with `flask --app schema_man run` (add `--debug` for debug mode).
- Run tests with `pytest`. No tests or lint/typecheck/CI configuration are currently checked in.
