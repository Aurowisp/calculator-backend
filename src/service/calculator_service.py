"""Application service for calculator use cases."""

from sqlalchemy.orm import Session

from src.calculator.evaluator import Number, evaluate
from src.calculator.exceptions import (
    DivisionByZeroError,
    InvalidExpressionError,
)
from src.calculator.parser import parse
from src.service.history_service import (
    HistoryPersistenceError,
    HistoryService,
)


MAX_EXPRESSION_LENGTH = 200


class CalculationServiceError(Exception):
    """Represent a calculator error at the application-service boundary."""


class CalculationPersistenceError(Exception):
    """Represent a history persistence failure after calculation."""


class CalculatorService:
    """Coordinate validation, parsing, and evaluation."""

    def __init__(self, history_service: HistoryService | None = None) -> None:
        self._history_service = history_service or HistoryService()

    def calculate(
        self,
        expression: str,
        database_session: Session,
    ) -> Number:
        """Calculate a valid expression and persist its result."""
        if len(expression) > MAX_EXPRESSION_LENGTH:
            message = (
                "Expression must not exceed "
                f"{MAX_EXPRESSION_LENGTH} characters"
            )
            raise CalculationServiceError(message)

        normalized_expression = expression.strip()

        if not normalized_expression:
            raise CalculationServiceError("Expression must not be empty")

        try:
            syntax_tree = parse(normalized_expression)
            result = evaluate(syntax_tree)
        except DivisionByZeroError as error:
            raise CalculationServiceError("Division by zero") from error
        except InvalidExpressionError as error:
            raise CalculationServiceError("Invalid expression") from error

        try:
            self._history_service.save_history(
                database_session,
                expression,
                result,
            )
        except HistoryPersistenceError as error:
            raise CalculationPersistenceError(
                "Unable to save calculation history"
            ) from error

        return result
