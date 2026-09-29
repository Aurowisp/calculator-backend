"""API tests for the Phase 3 calculation endpoint."""

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
    ],
)
def test_calculate_success(expression: str, expected_result: int) -> None:
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
    ("expression", "expected_message"),
    [
        ("10/0", "Division by zero"),
        ("", "Expression must not be empty"),
        ("   ", "Expression must not be empty"),
        ("abc", "Invalid character"),
        ("1+", "Expected a number"),
    ],
)
def test_calculate_rejects_invalid_expression(
    expression: str,
    expected_message: str,
) -> None:
    response = client.post(
        "/api/calculate",
        json={"expression": expression},
    )

    assert response.status_code == 400
    assert response.json()["success"] is False
    assert expected_message in response.json()["message"]


def test_calculate_requires_expression_field() -> None:
    response = client.post("/api/calculate", json={})

    assert response.status_code == 422


def test_calculate_rejects_non_string_expression() -> None:
    response = client.post("/api/calculate", json={"expression": 123})

    assert response.status_code == 422


def test_calculate_observes_operator_precedence() -> None:
    response = client.post(
        "/api/calculate",
        json={"expression": "1+2*3"},
    )

    assert response.status_code == 200
    assert response.json()["result"] == 7
