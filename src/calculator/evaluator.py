"""Evaluator for calculator syntax trees."""

from src.calculator.exceptions import (
    DivisionByZeroError,
    InvalidExpressionError,
)
from src.calculator.parser import (
    BinaryOperationNode,
    ExpressionNode,
    NumberNode,
)


Number = int | float


def evaluate(node: ExpressionNode) -> Number:
    """Evaluate a parser-produced syntax tree without executing source code."""
    if isinstance(node, NumberNode):
        return node.value

    if not isinstance(node, BinaryOperationNode):
        raise InvalidExpressionError("Unsupported expression node")

    left = evaluate(node.left)
    right = evaluate(node.right)

    if node.operator == "+":
        return left + right
    if node.operator == "-":
        return left - right
    if node.operator == "*":
        return left * right
    if node.operator == "/":
        if right == 0:
            raise DivisionByZeroError("Division by zero")
        result = left / right
        return int(result) if result.is_integer() else result

    raise InvalidExpressionError(f"Unsupported operator: {node.operator!r}")
