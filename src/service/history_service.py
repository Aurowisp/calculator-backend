"""Application service for calculation history persistence."""

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.calculator.evaluator import Number
from src.model.history import CalculationHistory


class HistoryServiceError(Exception):
    """Base exception for history service failures."""


class HistoryNotFoundError(HistoryServiceError):
    """Raised when a requested history record does not exist."""


class HistoryPersistenceError(HistoryServiceError):
    """Raised when a database operation cannot be completed."""


class HistoryService:
    """Save, list, and delete calculation history records."""

    def save_history(
        self,
        database_session: Session,
        expression: str,
        result: Number,
    ) -> CalculationHistory:
        """Persist one successful calculation and return its record."""
        history_record = CalculationHistory(
            expression=expression,
            result=result,
        )

        try:
            database_session.add(history_record)
            database_session.commit()
            database_session.refresh(history_record)
        except SQLAlchemyError as error:
            database_session.rollback()
            raise HistoryPersistenceError(
                "Unable to save calculation history"
            ) from error

        return history_record

    def get_history(
        self,
        database_session: Session,
    ) -> list[CalculationHistory]:
        """Return all history records with the newest ID first."""
        statement = select(CalculationHistory).order_by(
            CalculationHistory.id.desc()
        )

        try:
            return list(database_session.scalars(statement).all())
        except SQLAlchemyError as error:
            database_session.rollback()
            raise HistoryPersistenceError(
                "Unable to load calculation history"
            ) from error

    def delete_history(
        self,
        database_session: Session,
        history_id: int,
    ) -> None:
        """Delete one history record or report that it does not exist."""
        try:
            history_record = database_session.get(
                CalculationHistory,
                history_id,
            )
            if history_record is None:
                raise HistoryNotFoundError("History record not found")

            database_session.delete(history_record)
            database_session.commit()
        except HistoryNotFoundError:
            raise
        except SQLAlchemyError as error:
            database_session.rollback()
            raise HistoryPersistenceError(
                "Unable to delete calculation history"
            ) from error
