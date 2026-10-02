# Calculator Backend

## Overview

This repository contains the API and persistence service for a
front-end/back-end separated calculator course project. It validates and parses
expressions, evaluates them without dynamic code execution, stores successful
calculations, and exposes history operations to the separate browser client.

## Live Services

- Backend API: <https://calculator-backend-1m81.onrender.com>
- Health check: <https://calculator-backend-1m81.onrender.com/health>
- Swagger UI: <https://calculator-backend-1m81.onrender.com/docs>
- Backend repository: <https://github.com/Aurowisp/calculator-backend>
- Frontend: <https://aurowisp.github.io/calculator-frontend/>
- Frontend repository: <https://github.com/Aurowisp/calculator-frontend>

## Technology

- Python 3.11
- FastAPI
- Uvicorn
- SQLAlchemy 2
- Pydantic 2
- SQLite for local development
- PostgreSQL support through `psycopg`
- Pytest

## Architecture

```text
calculator-backend/
|-- src/
|   |-- main.py                 # FastAPI app, CORS, lifespan, health routes
|   |-- calculator/
|   |   |-- parser.py           # Tokenization and recursive-descent parsing
|   |   |-- evaluator.py        # Decimal-based AST evaluation
|   |   `-- exceptions.py       # Domain exceptions
|   |-- controller/
|   |   |-- calculator_controller.py
|   |   `-- history_controller.py
|   |-- service/
|   |   |-- calculator_service.py
|   |   `-- history_service.py
|   |-- model/
|   |   |-- calculation.py      # Calculation request/response schemas
|   |   |-- history.py          # SQLAlchemy history model
|   |   `-- history_schema.py   # History API schemas
|   `-- database/
|       `-- database.py         # Engine, sessions, and table initialization
|-- tests/
|-- requirements.txt
|-- .env.example
|-- .python-version
|-- README.md
|-- codestyle.md
`-- .gitignore
```

Layer responsibilities:

- **Controller** defines HTTP routes, dependencies, response schemas, and
  status-code mapping.
- **Service** coordinates calculation and persistence workflows.
- **Calculator** tokenizes, parses, and evaluates expression syntax.
- **Model** defines API schemas and the database entity.
- **Database** owns connection configuration, sessions, and initialization.

## Local Setup

### Create a Virtual Environment

```powershell
python -m venv venv
venv\Scripts\activate
```

On macOS or Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure the Environment

The service reads configuration from environment variables. It does not load a
`.env` file automatically. Copy values from `.env.example` into your shell or
hosting provider as needed.

| Variable | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | Local `calculator.db` SQLite file | Database connection |
| `CORS_ORIGINS` | Local frontend origins | Comma-separated allowed origins |

PowerShell example:

```powershell
$env:DATABASE_URL = "sqlite:///./calculator.db"
$env:CORS_ORIGINS = "http://localhost:5500,https://aurowisp.github.io"
```

PostgreSQL URLs beginning with `postgres://` or `postgresql://` are normalized
to SQLAlchemy's `postgresql+psycopg://` driver URL.

### Initialize the Database

No separate migration command is required for the current schema. The FastAPI
lifespan calls `initialize_database()` at startup and creates missing tables.

The history table stores:

- `id`
- `expression`
- `result`
- `created_at`

### Start the Server

```bash
uvicorn src.main:app --reload
```

Open:

- API root: <http://localhost:8000/>
- Health check: <http://localhost:8000/health>
- Swagger UI: <http://localhost:8000/docs>
- OpenAPI schema: <http://localhost:8000/openapi.json>

Expected root response:

```json
{
  "message": "Calculator Backend Running"
}
```

## API Reference

### Calculate

`POST /api/calculate`

Request:

```json
{
  "expression": "(1.2+3.4)*2"
}
```

Successful response:

```json
{
  "success": true,
  "expression": "(1.2+3.4)*2",
  "result": 9.2
}
```

A successful calculation is saved before the response is returned. Invalid
syntax and division by zero return `400`. A persistence failure returns `500`
and is not reported as a successful calculation.

### List History

`GET /api/history`

Returns history records ordered newest first.

```json
[
  {
    "id": 1,
    "expression": "1+2",
    "result": 3,
    "created_at": "2026-10-03T10:00:00"
  }
]
```

### Delete History

`DELETE /api/history/{id}`

Successful response:

```json
{
  "success": true,
  "message": "History record deleted"
}
```

A missing record returns `404`.

Expected API status codes:

| Status | Meaning |
| --- | --- |
| `200` | Calculation, history query, or deletion succeeded |
| `400` | The expression is invalid or attempts division by zero |
| `404` | The requested history record does not exist |
| `422` | The request body or path parameter failed validation |
| `500` | Persistence or another internal operation failed |

## Expression Rules

Supported syntax:

- `+`, `-`, `*`, and `/`
- parentheses
- decimal values
- unary `+` and `-`
- standard operator precedence

The maximum accepted expression length is 200 characters. Whitespace is
allowed, but implicit multiplication such as `2(3+4)` is not supported.

The parser follows this grammar:

```text
expression -> term (("+" | "-") term)*
term       -> unary (("*" | "/") unary)*
unary      -> ("+" | "-") unary | primary
primary    -> NUMBER | "(" expression ")"
```

The parser is a bounded recursive-descent parser. It rejects malformed or
unsupported input and does not use `eval()`, `exec()`, `compile()`, or other
dynamic code execution.

Evaluation uses Python `Decimal` with an internal precision of 256 digits.
Integral API results are serialized as JSON integers; non-integral results are
serialized as JSON floating-point values at the API boundary. This avoids the
common binary artifact for cases such as `0.1 + 0.2` while preserving a simple
JSON contract for the frontend.

## CORS

Without `CORS_ORIGINS`, these development origins are allowed:

- `http://localhost:5500`
- `http://127.0.0.1:5500`

For deployment, set the exact comma-separated frontend origins. Do not include
paths. Trailing slashes are normalized by the application.

## Tests

Run from the repository root with the virtual environment active:

```bash
python -m pytest -q
```

Current verified result: **93 tests passed**.

The suite covers:

- parser and evaluator behavior
- operator precedence, parentheses, decimals, and unary operators
- invalid expressions, limits, and division by zero
- calculation API schemas and error responses
- history persistence, ordering, deletion, and rollback paths
- CORS and deployment configuration
- health checks and internal error handling

One upstream Starlette deprecation warning may appear with the installed
dependency set; it does not affect the result.

## Deployment

The service is suitable for a Python web host such as Render.

Recommended commands:

```text
Build: pip install -r requirements.txt
Start: uvicorn src.main:app --host 0.0.0.0 --port $PORT
Health path: /health
```

Set at least:

- `DATABASE_URL` to a persistent managed PostgreSQL database
- `CORS_ORIGINS` to the deployed frontend origin

Do not use a host's ephemeral local filesystem for production history. Keep
credentials in the hosting provider's secret configuration, never in Git.

The current public deployment is:

```text
https://calculator-backend-1m81.onrender.com
```

## Engineering Constraints

- Keep HTTP handling, orchestration, parsing, persistence, and models in their
  existing layers.
- Never evaluate user input as Python code.
- Return stable JSON error messages without internal stack traces.
- Commit no database files, virtual environments, credentials, or local caches.
- Keep application code and documentation in English.

See [codestyle.md](codestyle.md) for the backend conventions.
