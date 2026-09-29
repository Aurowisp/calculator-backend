"""Application service for calculator use cases."""

from src.calculator.evaluator import Number, evaluate
from src.calculator.exceptions import CalculatorError
from src.calculator.parser import parse


class CalculationServiceError(Exception):
    """Represent a calculator error at the application-service boundary."""


class CalculatorService:
    """Coordinate validation, parsing, and evaluation."""

    def calculate(self, expression: str) -> Number:
        """Calculate a non-empty expression through the calculator layer."""
        normalized_expression = expression.strip()

        if not normalized_expression:
            raise CalculationServiceError("Expression must not be empty")

        try:
            syntax_tree = parse(normalized_expression)
            return evaluate(syntax_tree)
        except CalculatorError as error:
            raise CalculationServiceError(str(error)) from error
