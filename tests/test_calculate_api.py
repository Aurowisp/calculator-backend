"""API tests for the complete arithmetic expression parser."""

from typing import Any

import pytest
from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


@pytest.mark.parametrize(
    ("expression", "expected_result"),
    [
        ("1+2", 3),
        ("5-3", 2),
        ("4*6", 24),
        ("8/2", 4),
        ("1+2*3", 7),
        ("10-6/2", 7),
        ("8/2*3", 12),
        ("2*3+4*5", 26),
        ("8/4/2", 1),
        ("10-3-2", 5),
        ("(1+2)*3", 9),
        ("1+(2*3)", 7),
        ("((1+2)*3)+4", 13),
        ("2*(3+(4*5))", 46),
        ("1.5+2.3", 3.8),
        ("5/2", 2.5),
        (".5+1.5", 2),
        ("-5+8", 3),
        ("3*-2", -6),
        ("3--2", 5),
        ("-(2+3)", -5),
        ("-(-3)", 3),
        ("+5", 5),
        ("2*+3", 6),
        (" 1 +\t2 * 3 ", 7),
    ],
)
def test_calculate_success(
    expression: str,
    expected_result: int | float,
) -> None:
    response = client.post(
        "/api/calculate",
        json={"expression": expression},
    )

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "expression": expression,
        "result": expected_result,
    }


@pytest.mark.parametrize(
    "expression",
    [
        "abc",
        "1+a",
        "1+*2",
        "1++*2",
        "*",
        "/",
        "()",
        "( )",
        "(1+2",
        "1+2)",
        "((1+2)",
        "1.2.3",
        "..",
        "5..2",
        "1 2",
        "2(3+4)",
    ],
)
def test_calculate_rejects_invalid_expression(expression: str) -> None:
    response = client.post(
        "/api/calculate",
        json={"expression": expression},
    )

    assert response.status_code == 400
    assert response.json() == {
        "success": False,
        "message": "Invalid expression",
    }


@pytest.mark.parametrize(
    "expression",
    ["10/0", "1/(2-2)", "10/(3-3)"],
)
def test_calculate_rejects_division_by_zero(expression: str) -> None:
    response = client.post(
        "/api/calculate",
        json={"expression": expression},
    )

    assert response.status_code == 400
    assert response.json() == {
        "success": False,
        "message": "Division by zero",
    }


@pytest.mark.parametrize("expression", ["", "   ", "\t"])
def test_calculate_rejects_empty_expression(expression: str) -> None:
    response = client.post(
        "/api/calculate",
        json={"expression": expression},
    )

    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["message"] == "Expression must not be empty"


def test_calculate_rejects_expression_over_length_limit() -> None:
    response = client.post(
        "/api/calculate",
        json={"expression": "1" * 201},
    )

    assert response.status_code == 400
    assert response.json()["success"] is False
    assert "200 characters" in response.json()["message"]


@pytest.mark.parametrize("body", [{}, {"expression": 123}])
def test_calculate_validates_request_model(body: dict[str, Any]) -> None:
    response = client.post("/api/calculate", json=body)

    assert response.status_code == 422
