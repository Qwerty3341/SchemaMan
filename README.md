# SchemaMan

SQL Schemas normalizator (Like an interpreter for normal forms)
the system will generate reports for compliance and non-compliance for normal forms

## Languages

Python + Flask

## Architecture

Pipe and Filter

## Libs

- sqlglot (SQL sintax verification)
- jinja
- pytest

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

### Install JavaScript dependencies and build CodeMirror

Install Node.js (which includes npm) first. From the project root, install the
locked JavaScript dependencies and bundle the CodeMirror editor for Flask to
serve:

```shell
npm ci
npx esbuild schema_man/static/js/codeEditor.js --bundle --outfile=schema_man/static/js/codeEditor.bundle.js
```

Run the esbuild command again whenever `schema_man/static/js/codeEditor.js`
changes. The Flask template loads the generated `codeEditor.bundle.js` file.

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
