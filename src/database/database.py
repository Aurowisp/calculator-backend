"""SQLAlchemy configuration and database session management."""

import os
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_PATH = PROJECT_ROOT / "calculator.db"
DEFAULT_DATABASE_URL = f"sqlite:///{DEFAULT_DATABASE_PATH.as_posix()}"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""


def create_database_engine(database_url: str) -> Engine:
    """Create an engine with SQLite-specific thread configuration."""
    connect_args = (
        {"check_same_thread": False}
        if database_url.startswith("sqlite")
        else {}
    )
    return create_engine(database_url, connect_args=connect_args)


engine = create_database_engine(DATABASE_URL)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """Provide one database session and always close it after the request."""
    database_session = SessionLocal()
    try:
        yield database_session
    finally:
        database_session.close()


def initialize_database() -> None:
    """Create application tables that do not yet exist."""
    from src.model import history  # noqa: F401

    Base.metadata.create_all(bind=engine)
