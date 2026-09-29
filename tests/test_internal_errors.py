"""Tests for safe HTTP responses when persistence operations fail."""

import pytest
from fastapi.testclient import TestClient

from src.controller import calculator_controller, history_controller
from src.service.calculator_service import CalculationPersistenceError
from src.service.history_service import HistoryPersistenceError


def test_calculation_persistence_error_returns_safe_500(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_calculation(*_args, **_kwargs):
        raise CalculationPersistenceError("private database details")

    monkeypatch.setattr(
        calculator_controller.calculator_service,
        "calculate",
        fail_calculation,
    )

    response = client.post(
        "/api/calculate",
        json={"expression": "1+2"},
    )

    assert response.status_code == 500
    assert response.json() == {
        "success": False,
        "message": "Unable to save calculation history",
    }
    assert "private database details" not in response.text


def test_history_read_error_returns_safe_500(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_history_read(*_args, **_kwargs):
        raise HistoryPersistenceError("private SQL details")

    monkeypatch.setattr(
        history_controller.history_service,
        "get_history",
        fail_history_read,
    )

    response = client.get("/api/history")

    assert response.status_code == 500
    assert response.json() == {
        "success": False,
        "message": "Unable to load calculation history",
    }
    assert "private SQL details" not in response.text


def test_history_delete_error_returns_safe_500(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_history_delete(*_args, **_kwargs):
        raise HistoryPersistenceError("private SQLite path")

    monkeypatch.setattr(
        history_controller.history_service,
        "delete_history",
        fail_history_delete,
    )

    response = client.delete("/api/history/1")

    assert response.status_code == 500
    assert response.json() == {
        "success": False,
        "message": "Unable to delete calculation history",
    }
    assert "private SQLite path" not in response.text
