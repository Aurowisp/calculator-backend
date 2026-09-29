"""CORS tests for supported frontend development origins."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    "origin",
    [
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
)
def test_frontend_development_origin_is_allowed(
    client: TestClient,
    origin: str,
) -> None:
    response = client.options(
        "/api/calculate",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin
