# SchemaMan

SQL schema normalizer — generates compliance reports for normal forms (1NF–5NF). Does not generate SQL code.

## Tech

Python 3.14, Flask (App Factory pattern), sqlglot for SQL parsing. DB engines: SQLite, MariaDB.

## Key patterns

- Entry point: `schema_man/__init__.py:create_app()` — always use the app factory, never instantiate Flask directly.
- Routes live in `schema_man/schema_man.py` as a Blueprint (`bp`).
- Instance config: `instance/config.py` (gitignored, created at runtime).

## Commands

No `requirements.txt` or `pyproject.toml` exists yet. Dependencies are listed only in README. Install manually if needed:

```
pip install flask sqlglot pytest
```

Run the dev server:

```
flask --app schema_man run
```

Run tests (once `tests/` is populated):

```
pytest
```

## Notes

- `tests/` directory is empty — no tests exist yet.
- No linter, formatter, or CI configured.
- `NormalForms.md` contains the domain knowledge (in Spanish) for normal form rules.
