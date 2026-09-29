"""SQLAlchemy model for persisted calculation history."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Index, Integer, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database.database import Base


def current_utc_time() -> datetime:
    """Return a timezone-naive UTC timestamp for SQLite storage."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class CalculationHistory(Base):
    """Represent one successful calculator operation."""

    __tablename__ = "calculation_history"
    __table_args__ = (Index("ix_calculation_history_id", "id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    expression: Mapped[str] = mapped_column(Text, nullable=False)
    result: Mapped[int | float] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=current_utc_time,
    )
