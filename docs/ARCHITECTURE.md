# Architecture

SchemaMan follows a **Pipe and Filter** pattern (`schema_man/pipeline/`).
A single context object travels through ordered filters; each filter reads
it, adds results to it, and passes it on.

## Flow

    POST /api/parse-sql (schema_man/api.py)
        |
        v
    PipeLineContext(sql, dialect, target_normal_form)
        |
        v
    Pipe([ParseSqlFilter, ModelSchemaFilter, ...])
        |   context = filter.apply(context)   # one by one, in order
        v
    Context with results -> JSON response

## Core pieces (schema_man/pipeline/)

- `pipe.py` - `Pipe`: holds the list of filters; `run(context)` applies them
  in order, threading the context through each one:

  ```python
  class Pipe:

      def __init__(self, filters):
          self.filters = filters

      def run(self, context):
          for f in self.filters:
              context = f.apply(context)
          return context
  ```

- `filter.py` - `Filter` (ABC): the contract every filter must implement,
  `apply(context) -> context`.
- `context.py` - `PipeLineContext`: the data that circulates through the pipe.
  - Inputs: `sql`, `dialect`, `target_normal_form`
  - Results: `sql_checked`, `schema`, `violations`, `report`
- `filters/` - one module per pipeline step.
