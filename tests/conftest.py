"""Shared pytest fixtures with an isolated SQLite database."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.database.database import Base, create_database_engine, get_db
from src.main import app


@pytest.fixture
def test_engine(tmp_path) -> Generator[Engine, None, None]:
    """Create a separate file-backed SQLite database for each test."""
    database_path = tmp_path / "test_calculator.db"
    database_url = f"sqlite:///{database_path.as_posix()}"
    database_engine = create_database_engine(database_url)
    Base.metadata.create_all(bind=database_engine)

    try:
        yield database_engine
    finally:
        database_engine.dispose()


@pytest.fixture
def test_session_factory(
    test_engine: Engine,
) -> sessionmaker[Session]:
    """Create sessions bound only to the current test database."""
    return sessionmaker(
        bind=test_engine,
        autoflush=False,
        expire_on_commit=False,
    )


@pytest.fixture
def client(
    test_session_factory: sessionmaker[Session],
) -> Generator[TestClient, None, None]:
    """Override the application database dependency for API tests."""

    def override_get_db() -> Generator[Session, None, None]:
        database_session = test_session_factory()
        try:
            yield database_session
        finally:
            database_session.close()

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)

    try:
        yield test_client
    finally:
        test_client.close()
        app.dependency_overrides.clear()
