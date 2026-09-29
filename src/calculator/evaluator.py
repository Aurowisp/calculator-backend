"""Evaluator for calculator syntax trees."""

from src.calculator.exceptions import (
    DivisionByZeroError,
    InvalidExpressionError,
)
from src.calculator.parser import (
    BinaryOperationNode,
    ExpressionNode,
    NumberNode,
    UnaryOperationNode,
)


Number = int | float


def evaluate(node: ExpressionNode) -> Number:
    """Evaluate and normalize a parser-produced syntax tree."""
    result = _evaluate_node(node)

    if isinstance(result, float) and result.is_integer():
        return int(result)

    return result


def _evaluate_node(node: ExpressionNode) -> Number:
    """Recursively execute only known syntax-tree node types."""
    if isinstance(node, NumberNode):
        return node.value

    if isinstance(node, UnaryOperationNode):
        operand = _evaluate_node(node.operand)

        if node.operator == "+":
            return operand
        if node.operator == "-":
            return -operand

        raise InvalidExpressionError(
            f"Unsupported unary operator: {node.operator!r}"
        )

    if not isinstance(node, BinaryOperationNode):
        raise InvalidExpressionError("Unsupported expression node")

    left = _evaluate_node(node.left)
    right = _evaluate_node(node.right)

    if node.operator == "+":
        return left + right
    if node.operator == "-":
        return left - right
    if node.operator == "*":
        return left * right
    if node.operator == "/":
        if right == 0:
            raise DivisionByZeroError("Division by zero")
        return left / right

    raise InvalidExpressionError(f"Unsupported operator: {node.operator!r}")
