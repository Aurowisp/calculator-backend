"""Exceptions raised by the calculator domain layer."""


class CalculatorError(Exception):
    """Base exception for expected calculator errors."""


class InvalidExpressionError(CalculatorError):
    """Raised when an expression cannot be parsed safely."""


class DivisionByZeroError(CalculatorError):
    """Raised when an expression attempts to divide by zero."""
