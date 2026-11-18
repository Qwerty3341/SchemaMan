# SchemaMan

<div align="center">
    <img src="schema_man/static/img/WholeLogo.webp" alt="Schema Man Logo" width="300"/>
</div>

## The normal forms interpreter
Schema man is a system written in flask that detects normal forms in SQL schemas.

## Languages

Python + Flask

## Architecture

Pipe and Filter

## Libs

- sqlglot (SQL sintax verification)
- jinja
- pytest
- codemirror (node)

## DB engines

- SQLite
- MariaDB

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

### Run tests

```shell
pytest
```
