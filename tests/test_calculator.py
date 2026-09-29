"""Unit tests for the framework-independent calculator layer."""

import pytest

from src.calculator.evaluator import evaluate
from src.calculator.exceptions import (
    DivisionByZeroError,
    InvalidExpressionError,
)
from src.calculator.parser import parse


@pytest.mark.parametrize(
    ("expression", "expected_result"),
    [
        ("2*3+4*5", 26),
        ("8/4/2", 1),
        ("2*(3+(4*5))", 46),
        ("1.5+2.3", 3.8),
        ("3*-2", -6),
        ("3--2", 5),
        ("-(-3)", 3),
    ],
)
def test_parser_and_evaluator(
    expression: str,
    expected_result: int | float,
) -> None:
    assert evaluate(parse(expression)) == expected_result


@pytest.mark.parametrize(
    "expression",
    ["abc", "()", "(1+2", "1+2)", "1.2.3", "1 2"],
)
def test_parser_rejects_invalid_expression(expression: str) -> None:
    with pytest.raises(InvalidExpressionError):
        parse(expression)


def test_evaluator_rejects_division_by_zero() -> None:
    with pytest.raises(DivisionByZeroError, match="Division by zero"):
        evaluate(parse("1/(2-2)"))
