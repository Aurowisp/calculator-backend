"""Safe parser for basic arithmetic expressions.

The grammar intentionally supports integers and the four basic binary
operators only. Parentheses, decimal numbers, and unary operators are reserved
for the next parser phase.
"""

from dataclasses import dataclass
from typing import TypeAlias

from src.calculator.exceptions import InvalidExpressionError


NUMBER = "NUMBER"
OPERATOR = "OPERATOR"
END = "END"


@dataclass(frozen=True)
class Token:
    """Represent one token from the source expression."""

    kind: str
    value: str


@dataclass(frozen=True)
class NumberNode:
    """Represent an integer literal in the syntax tree."""

    value: int


@dataclass(frozen=True)
class BinaryOperationNode:
    """Represent a binary operation in the syntax tree."""

    left: "ExpressionNode"
    operator: str
    right: "ExpressionNode"


ExpressionNode: TypeAlias = NumberNode | BinaryOperationNode


def tokenize(expression: str) -> list[Token]:
    """Convert a source expression into validated tokens."""
    tokens: list[Token] = []
    position = 0

    while position < len(expression):
        character = expression[position]

        if character.isspace():
            position += 1
            continue

        if character in "0123456789":
            start = position
            while (
                position < len(expression)
                and expression[position] in "0123456789"
            ):
                position += 1
            tokens.append(Token(NUMBER, expression[start:position]))
            continue

        if character in "+-*/":
            tokens.append(Token(OPERATOR, character))
            position += 1
            continue

        raise InvalidExpressionError(
            f"Invalid character at position {position}: {character!r}"
        )

    tokens.append(Token(END, ""))
    return tokens


class Parser:
    """Build a syntax tree while enforcing operator precedence."""

    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = tokens
        self._position = 0

    def parse(self) -> ExpressionNode:
        """Parse all tokens into a complete expression tree."""
        if self._current.kind == END:
            raise InvalidExpressionError("Expression must not be empty")

        node = self._parse_expression()

        if self._current.kind != END:
            raise InvalidExpressionError(
                f"Unexpected token: {self._current.value!r}"
            )

        return node

    @property
    def _current(self) -> Token:
        return self._tokens[self._position]

    def _advance(self) -> None:
        self._position += 1

    def _parse_expression(self) -> ExpressionNode:
        node = self._parse_term()

        while self._current.value in {"+", "-"}:
            operator = self._current.value
            self._advance()
            node = BinaryOperationNode(
                left=node,
                operator=operator,
                right=self._parse_term(),
            )

        return node

    def _parse_term(self) -> ExpressionNode:
        node = self._parse_factor()

        while self._current.value in {"*", "/"}:
            operator = self._current.value
            self._advance()
            node = BinaryOperationNode(
                left=node,
                operator=operator,
                right=self._parse_factor(),
            )

        return node

    def _parse_factor(self) -> ExpressionNode:
        token = self._current

        if token.kind != NUMBER:
            token_description = token.value or "end of expression"
            raise InvalidExpressionError(
                f"Expected a number, received {token_description!r}"
            )

        self._advance()
        return NumberNode(value=int(token.value))


def parse(expression: str) -> ExpressionNode:
    """Parse an expression into a safe syntax tree."""
    return Parser(tokenize(expression)).parse()
