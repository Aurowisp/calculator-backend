"""Calculator API routes."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.model.calculation import (
    CalculateErrorResponse,
    CalculateRequest,
    CalculateResponse,
)
from src.service.calculator_service import (
    CalculationPersistenceError,
    CalculationServiceError,
    CalculatorService,
)


router = APIRouter(
    prefix="/api",
    tags=["calculator"],
)

calculator_service = CalculatorService()


@router.post(
    "/calculate",
    response_model=CalculateResponse,
    responses={
        400: {
            "model": CalculateErrorResponse,
            "description": "Invalid mathematical expression",
        },
        500: {
            "model": CalculateErrorResponse,
            "description": "Calculation history persistence failure",
        },
    },
)
async def calculate_expression(
    request: CalculateRequest,
    database_session: Session = Depends(get_db),
) -> CalculateResponse | JSONResponse:
    """Calculate an expression or return a consistent client error."""
    try:
        result = calculator_service.calculate(
            request.expression,
            database_session,
        )
    except CalculationServiceError as error:
        error_response = CalculateErrorResponse(message=str(error))
        return JSONResponse(
            status_code=400,
            content=error_response.model_dump(),
        )
    except CalculationPersistenceError:
        error_response = CalculateErrorResponse(
            message="Unable to save calculation history"
        )
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump(),
        )

    return CalculateResponse(
        expression=request.expression,
        result=result,
    )
