# Backend Code Style

This project follows [PEP 8](https://peps.python.org/pep-0008/) and uses type
hints and explicit layer boundaries to keep the FastAPI service maintainable.

## Naming

- Use `snake_case` for modules, variables, functions, methods, and route handler
  names.
- Use `PascalCase` for classes, Pydantic schemas, and exception types.
- Use `UPPER_SNAKE_CASE` for module-level constants.
- Prefix internal helpers with a single underscore when they are not part of a
  module's public interface.
- Choose domain-specific names such as `database_session`, `history_id`, and
  `calculate_expression`.

## Formatting

- Use 4 spaces for indentation. Do not use tabs.
- Keep lines at 79 characters when practical.
- Put two blank lines between top-level definitions.
- Use one blank line between related methods inside a class.
- Include trailing commas in multiline collections and calls.
- Keep source files encoded as UTF-8.
- End every text file with one newline.

## Imports

Group imports in this order, separated by blank lines:

1. Python standard library
2. Third-party packages
3. Local application modules

Use absolute imports from `src`. Do not use wildcard imports. Import models for
SQLAlchemy metadata registration only where initialization requires them, and
document that intentional side effect.

## Type Hints and Functions

- Type all public function parameters and return values.
- Keep functions focused on one responsibility.
- Prefer explicit return types over implicit `Any`.
- Use `collections.abc` types for iterators and generators.
- Use FastAPI dependencies for request-scoped database sessions.
- Close resources deterministically, including error paths.

## Documentation and Comments

- Give each module a short English docstring.
- Give public functions, classes, and non-obvious helpers concise docstrings.
- Describe behavior and constraints, not syntax already visible in the code.
- Use comments sparingly for security limits, rollback behavior, compatibility,
  or other decisions that are not self-evident.
- Keep code, identifiers, comments, API text, and documentation in English.

## Architecture

- Controllers translate HTTP requests and exceptions into API responses.
- Services coordinate domain work and transaction boundaries.
- The calculator package owns tokenization, parsing, and evaluation.
- Models own Pydantic schemas and SQLAlchemy entities.
- The database package owns engines, sessions, and initialization.

Do not place parsing in controllers, HTTP response construction in services, or
business workflows in ORM models.

## FastAPI and API Design

- Define routers outside `main.py` and register them in the application entry
  point.
- Declare request and response schemas with Pydantic.
- Document non-success responses on each route.
- Return consistent JSON error objects.
- Do not expose exception details, SQL statements, credentials, or stack traces
  to clients.
- Keep health checks side-effect free.

## Database Practices

- Obtain sessions through `get_db()`.
- Commit only after the complete operation succeeds.
- Roll back after a failed write.
- Map persistence errors to service exceptions before they reach controllers.
- Keep database URLs and credentials in environment variables.
- Never commit SQLite database files or generated test databases.

## Calculator Safety

- Never use `eval()`, `exec()`, `compile()`, or dynamic code generation.
- Keep grammar limits explicit and covered by tests.
- Raise domain exceptions for invalid syntax, unsupported input, and division by
  zero.
- Use `Decimal` for internal arithmetic and make API-boundary conversion
  deliberate.

## Tests

- Use `pytest` and descriptive test names.
- Test public behavior and important failure paths.
- Keep tests independent through isolated temporary databases and dependency
  overrides.
- Verify rollback and session cleanup when persistence fails.
- Add regression tests with every bug fix.
- Run `python -m pytest -q` before release.
