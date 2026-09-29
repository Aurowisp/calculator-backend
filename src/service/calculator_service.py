"""Application service for calculator use cases."""

from src.calculator.evaluator import Number, evaluate
from src.calculator.exceptions import (
    DivisionByZeroError,
    InvalidExpressionError,
)
from src.calculator.parser import parse


MAX_EXPRESSION_LENGTH = 200


class CalculationServiceError(Exception):
    """Represent a calculator error at the application-service boundary."""


class CalculatorService:
    """Coordinate validation, parsing, and evaluation."""

    def calculate(self, expression: str) -> Number:
        """Calculate a non-empty expression through the calculator layer."""
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
            return evaluate(syntax_tree)
        except DivisionByZeroError as error:
            raise CalculationServiceError("Division by zero") from error
        except InvalidExpressionError as error:
            raise CalculationServiceError("Invalid expression") from error
