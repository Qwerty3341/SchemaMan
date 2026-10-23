# Tests

Run everything from the repository root. Activate the virtualenv first:

```shell
source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
```

## All tests

```shell
pytest
```

## One file at a time

```shell
# Type translation (SQL type -> generic type), by engine
pytest tests/test_data_types.py

# First filter: SQL syntax validation (ParseSqlFilter)
pytest tests/test_parse_sql.py

# ModelSchemaFilter with school.sql (SQLite)
pytest tests/test_model_schema.py

# ModelSchemaFilter with store.sql (MariaDB/MySQL)
pytest tests/test_store_schema.py
```

`test_model_schema.py` and `test_store_schema.py` print the generic schema
of their `.sql` file to the terminal on every run.

## Single test

Add `-v` to see test names, and use the node id:

```shell
pytest tests/test_parse_sql.py -v

pytest "tests/test_data_types.py::test_generic_type_of[sqlite-VARCHAR(50)-STRING]"

pytest tests/test_parse_sql.py::test_empty_sql_is_rejected
```

## Useful flags

```shell
pytest -v          # list each test
pytest -x          # stop on the first failure
pytest -k "store"  # run only tests whose name contains "store"
pytest --collect-only -q   # list tests without running them
```

## Notes

- `pytest.ini` at the root sets `pythonpath = .`, so plain `pytest` works
  without `python -m pytest`.
- New `.sql` fixtures go in `tests/schemas/`.
