# SchemaMan

SQL Schemas normalizator (Like an interpreter for normal forms)
the system will generate reports for compliance and non-compliance for normal forms
Is not expected that the system will generate code just the report

## Languages

Python + Flask

## Architecture

Using Flask the architecture will be conditioned for the
design pattern "App Factory" (Flask recommended design)

## Libs

- sqlglot (SQL sintax verification)
- jinja
- pytest
- WeasyPrint or reportlab (PDF download)

## DB engines

For tesis

- SQLite
- MariaDB

In future

- Postgres
- Oracle
- TSQL

## Links

Figma <https://www.figma.com/design/zzviQvjM2nXhJkRYw5AyfL/TreeQL?node-id=0-1&p=f&t=TDRe5j9R17Q8Xmqy-0>


## Commands

### Create and activate the virtual environment

Linux/macOS:

```shell
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Run system in debug mode

```shell
flask --app schema_man run --debug
```

### Run system without debug mode

```shell
flask --app schema_man run
```

The project does not currently configure a production WSGI server. Do not use
Flask's development server for production deployments.

### Run tests

```shell
pytest
```
