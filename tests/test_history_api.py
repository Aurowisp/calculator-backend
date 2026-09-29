"""Database-backed calculation history API tests."""

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.model.history import CalculationHistory


def test_empty_history_returns_empty_list(client: TestClient) -> None:
    response = client.get("/api/history")

    assert response.status_code == 200
    assert response.json() == []


def test_successful_calculation_saves_history(client: TestClient) -> None:
    calculate_response = client.post(
        "/api/calculate",
        json={"expression": "1+2"},
    )
    history_response = client.get("/api/history")

    assert calculate_response.status_code == 200
    assert history_response.status_code == 200
    assert len(history_response.json()) == 1
    assert history_response.json()[0]["expression"] == "1+2"
    assert history_response.json()[0]["result"] == 3
    assert history_response.json()[0]["created_at"]


def test_decimal_result_is_saved_without_binary_float_artifact(
    client: TestClient,
) -> None:
    calculate_response = client.post(
        "/api/calculate",
        json={"expression": "2.3+5.6"},
    )
    history_response = client.get("/api/history")

    assert calculate_response.status_code == 200
    assert calculate_response.json()["result"] == 7.9
    assert history_response.status_code == 200
    assert history_response.json()[0]["expression"] == "2.3+5.6"
    assert history_response.json()[0]["result"] == 7.9
    assert isinstance(history_response.json()[0]["result"], float)


def test_multiple_records_are_returned_newest_first(
    client: TestClient,
) -> None:
    expressions = ["1+2", "5*8", "(1+2)*3"]

    for expression in expressions:
        response = client.post(
            "/api/calculate",
            json={"expression": expression},
        )
        assert response.status_code == 200

    history = client.get("/api/history").json()

    assert [record["expression"] for record in history] == list(
        reversed(expressions)
    )
    assert [record["result"] for record in history] == [9, 40, 3]


def test_invalid_calculation_does_not_save_history(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/calculate",
        json={"expression": "abc"},
    )

    assert response.status_code == 400
    assert client.get("/api/history").json() == []


def test_division_by_zero_does_not_save_history(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/calculate",
        json={"expression": "10/0"},
    )

    assert response.status_code == 400
    assert client.get("/api/history").json() == []


def test_delete_existing_history_record(client: TestClient) -> None:
    client.post("/api/calculate", json={"expression": "1+2"})
    history_record = client.get("/api/history").json()[0]

    delete_response = client.delete(
        f"/api/history/{history_record['id']}"
    )

    assert delete_response.status_code == 200
    assert delete_response.json() == {
        "success": True,
        "message": "History record deleted",
    }
    assert client.get("/api/history").json() == []


def test_delete_missing_history_record_returns_404(
    client: TestClient,
) -> None:
    response = client.delete("/api/history/999999")

    assert response.status_code == 404
    assert response.json() == {
        "success": False,
        "message": "History record not found",
    }


def test_integer_and_decimal_results_remain_json_numbers(
    client: TestClient,
) -> None:
    client.post("/api/calculate", json={"expression": "1+2"})
    client.post("/api/calculate", json={"expression": "5/2"})

    history = client.get("/api/history").json()

    assert history[0]["result"] == 2.5
    assert isinstance(history[0]["result"], float)
    assert history[1]["result"] == 3
    assert isinstance(history[1]["result"], int)


def test_history_is_stored_in_file_database(
    client: TestClient,
    test_engine: Engine,
) -> None:
    client.post("/api/calculate", json={"expression": "1+2"})

    second_engine = create_engine(
        str(test_engine.url),
        connect_args={"check_same_thread": False},
    )
    second_session_factory = sessionmaker(bind=second_engine)

    try:
        with second_session_factory() as database_session:
            count = database_session.scalar(
                select(func.count()).select_from(CalculationHistory)
            )
            record = database_session.scalar(select(CalculationHistory))
    finally:
        second_engine.dispose()

    assert count == 1
    assert record is not None
    assert record.expression == "1+2"
    assert record.result == 3
