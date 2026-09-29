"""Calculation history API routes."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.model.history_schema import (
    DeleteHistoryResponse,
    HistoryErrorResponse,
    HistoryResponse,
)
from src.service.history_service import (
    HistoryNotFoundError,
    HistoryPersistenceError,
    HistoryService,
)


router = APIRouter(
    prefix="/api/history",
    tags=["history"],
)

history_service = HistoryService()


@router.get(
    "",
    response_model=list[HistoryResponse],
    responses={
        500: {
            "model": HistoryErrorResponse,
            "description": "History database failure",
        }
    },
)
async def get_calculation_history(
    database_session: Session = Depends(get_db),
) -> list[HistoryResponse] | JSONResponse:
    """Return calculation history with newest records first."""
    try:
        records = history_service.get_history(database_session)
    except HistoryPersistenceError:
        return _error_response(500, "Unable to load calculation history")

    return [HistoryResponse.model_validate(record) for record in records]


@router.delete(
    "/{history_id}",
    response_model=DeleteHistoryResponse,
    responses={
        404: {
            "model": HistoryErrorResponse,
            "description": "History record not found",
        },
        500: {
            "model": HistoryErrorResponse,
            "description": "History database failure",
        },
    },
)
async def delete_calculation_history(
    history_id: int,
    database_session: Session = Depends(get_db),
) -> DeleteHistoryResponse | JSONResponse:
    """Delete one calculation history record by ID."""
    try:
        history_service.delete_history(database_session, history_id)
    except HistoryNotFoundError:
        return _error_response(404, "History record not found")
    except HistoryPersistenceError:
        return _error_response(500, "Unable to delete calculation history")

    return DeleteHistoryResponse()


def _error_response(status_code: int, message: str) -> JSONResponse:
    """Build a consistent history error response."""
    error_response = HistoryErrorResponse(message=message)
    return JSONResponse(
        status_code=status_code,
        content=error_response.model_dump(),
    )
