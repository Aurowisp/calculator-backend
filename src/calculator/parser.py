"""Tokenizer and recursive descent parser for arithmetic expressions."""

from dataclasses import dataclass
from typing import TypeAlias

from src.calculator.exceptions import InvalidExpressionError


NUMBER = "NUMBER"
PLUS = "PLUS"
MINUS = "MINUS"
MULTIPLY = "MULTIPLY"
DIVIDE = "DIVIDE"
LEFT_PARENTHESIS = "LEFT_PARENTHESIS"
RIGHT_PARENTHESIS = "RIGHT_PARENTHESIS"
END_OF_INPUT = "END_OF_INPUT"

SINGLE_CHARACTER_TOKENS = {
    "+": PLUS,
    "-": MINUS,
    "*": MULTIPLY,
    "/": DIVIDE,
    "(": LEFT_PARENTHESIS,
    ")": RIGHT_PARENTHESIS,
}


@dataclass(frozen=True)
class Token:
    """Represent one token from the source expression."""

    kind: str
    value: str


@dataclass(frozen=True)
class NumberNode:
    """Represent an integer or decimal literal in the syntax tree."""

    value: int | float


@dataclass(frozen=True)
class BinaryOperationNode:
    """Represent a binary operation in the syntax tree."""

    left: "ExpressionNode"
    operator: str
    right: "ExpressionNode"


@dataclass(frozen=True)
class UnaryOperationNode:
    """Represent a unary plus or minus operation in the syntax tree."""

    operator: str
    operand: "ExpressionNode"


ExpressionNode: TypeAlias = (
    NumberNode | BinaryOperationNode | UnaryOperationNode
)


def tokenize(expression: str) -> list[Token]:
    """Convert a source expression into validated tokens."""
    tokens: list[Token] = []
    position = 0

    while position < len(expression):
        character = expression[position]

        if character.isspace():
            position += 1
            continue

        if character in "0123456789.":
            number, position = _read_number(expression, position)
            tokens.append(Token(NUMBER, number))
            continue

        if character in SINGLE_CHARACTER_TOKENS:
            tokens.append(Token(SINGLE_CHARACTER_TOKENS[character], character))
            position += 1
            continue

        raise InvalidExpressionError(
            f"Invalid character at position {position}: {character!r}"
        )

    tokens.append(Token(END_OF_INPUT, ""))
    return tokens


def _read_number(expression: str, start: int) -> tuple[str, int]:
    """Read one integer or decimal token, including optional leading dot."""
    position = start
    digits_before_dot = 0
    digits_after_dot = 0

    while (
        position < len(expression)
        and expression[position] in "0123456789"
    ):
        digits_before_dot += 1
        position += 1

    if position < len(expression) and expression[position] == ".":
        position += 1
        while (
            position < len(expression)
            and expression[position] in "0123456789"
        ):
            digits_after_dot += 1
            position += 1

    if digits_before_dot == 0 and digits_after_dot == 0:
        raise InvalidExpressionError(f"Invalid number at position {start}")

    return expression[start:position], position


class Parser:
    """Build a syntax tree while enforcing operator precedence."""

    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = tokens
        self._position = 0

    def parse(self) -> ExpressionNode:
        """Parse all tokens into a complete expression tree."""
        if self._current.kind == END_OF_INPUT:
            raise InvalidExpressionError("Expression must not be empty")

        node = self._parse_expression()

        if self._current.kind != END_OF_INPUT:
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
        """Parse addition and subtraction, the lowest-precedence operators."""
        node = self._parse_term()

        while self._current.kind in {PLUS, MINUS}:
            operator = self._current.value
            self._advance()
            node = BinaryOperationNode(
                left=node,
                operator=operator,
                right=self._parse_term(),
            )

        return node

    def _parse_term(self) -> ExpressionNode:
        """Parse multiplication and division before additive operators."""
        node = self._parse_unary()

        while self._current.kind in {MULTIPLY, DIVIDE}:
            operator = self._current.value
            self._advance()
            node = BinaryOperationNode(
                left=node,
                operator=operator,
                right=self._parse_unary(),
            )

        return node

    def _parse_unary(self) -> ExpressionNode:
        """Bind unary signs more tightly than every binary operator."""
        if self._current.kind in {PLUS, MINUS}:
            operator = self._current.value
            self._advance()
            return UnaryOperationNode(
                operator=operator,
                operand=self._parse_unary(),
            )

        return self._parse_primary()

    def _parse_primary(self) -> ExpressionNode:
        """Parse a number or a parenthesized nested expression."""
        token = self._current

        if token.kind == NUMBER:
            self._advance()
            return NumberNode(value=_convert_number(token.value))

        if token.kind == LEFT_PARENTHESIS:
            self._advance()
            node = self._parse_expression()

            if self._current.kind != RIGHT_PARENTHESIS:
                raise InvalidExpressionError("Missing closing parenthesis")

            self._advance()
            return node

        token_description = token.value or "end of expression"
        raise InvalidExpressionError(
            f"Expected a number or '(', received {token_description!r}"
        )


def _convert_number(value: str) -> int | float:
    """Convert a validated numeric token to a JSON-compatible number."""
    if "." in value:
        return float(value)
    return int(value)


def parse(expression: str) -> ExpressionNode:
    """Parse an expression into a safe syntax tree."""
    return Parser(tokenize(expression)).parse()
