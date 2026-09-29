"""Tests for deployment configuration and health checks."""

from pathlib import Path

from fastapi.testclient import TestClient

from src.database.database import (
    DEFAULT_DATABASE_PATH,
    DEFAULT_DATABASE_URL,
    create_database_engine,
    resolve_database_url,
)
from src.main import DEFAULT_CORS_ORIGINS, parse_cors_origins


def test_health_check_is_available(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_local_database_defaults_to_project_sqlite() -> None:
    assert resolve_database_url(None) == DEFAULT_DATABASE_URL
    assert resolve_database_url("  ") == DEFAULT_DATABASE_URL
    assert DEFAULT_DATABASE_PATH == (
        Path(__file__).resolve().parents[1] / "calculator.db"
    )


def test_postgresql_urls_use_psycopg_driver() -> None:
    expected_url = "postgresql+psycopg://user:password@host/database"

    assert (
        resolve_database_url("postgres://user:password@host/database")
        == expected_url
    )
    assert (
        resolve_database_url("postgresql://user:password@host/database")
        == expected_url
    )
    assert resolve_database_url(expected_url) == expected_url

    database_engine = create_database_engine(expected_url)
    try:
        assert database_engine.dialect.name == "postgresql"
        assert database_engine.dialect.driver == "psycopg"
    finally:
        database_engine.dispose()


def test_cors_origins_are_parsed_and_deduplicated() -> None:
    configured_origins = (
        "https://example.github.io/, http://localhost:5500, "
        "https://example.github.io"
    )

    assert parse_cors_origins(configured_origins) == [
        "https://example.github.io",
        "http://localhost:5500",
    ]
    assert parse_cors_origins(None) == list(DEFAULT_CORS_ORIGINS)
