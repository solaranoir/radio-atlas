# tests/unit/api/test_validation.py

from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.errors import APIError
from app.main import create_app


def _client(
    *,
    raise_server_exceptions: bool = True,
) -> TestClient:
    return TestClient(
        create_app(),
        raise_server_exceptions=raise_server_exceptions,
    )


def test_malformed_datetime_returns_standardized_422() -> None:
    client = _client()

    response = client.get(
        "/api/v1/observations",
        params={
            "start_time": "definitely-not-a-datetime",
        },
    )

    assert response.status_code == 422

    body = response.json()

    assert body["error"]["code"] == "validation_error"
    assert body["error"]["message"] == "Request validation failed"
    assert "details" in body["error"]


def test_invalid_limit_returns_standardized_422() -> None:
    client = _client()

    response = client.get(
        "/api/v1/observations",
        params={
            "limit": 0,
        },
    )

    assert response.status_code == 422

    body = response.json()

    assert body["error"]["code"] == "validation_error"
    assert body["error"]["message"] == "Request validation failed"
    assert "details" in body["error"]


def test_negative_offset_returns_standardized_422() -> None:
    client = _client()

    response = client.get(
        "/api/v1/observations",
        params={
            "offset": -1,
        },
    )

    assert response.status_code == 422

    body = response.json()

    assert body["error"]["code"] == "validation_error"
    assert body["error"]["message"] == "Request validation failed"
    assert "details" in body["error"]


def test_start_time_after_end_time_returns_400() -> None:
    client = _client()

    with patch(
        "app.api.routes.observations.list_observations",
        return_value=[],
    ) as list_observations:
        response = client.get(
            "/api/v1/observations",
            params={
                "start_time": "2026-08-24T12:00:00Z",
                "end_time": "2026-08-20T12:00:00Z",
            },
        )

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "invalid_time_range",
            "message": ("start_time must be before or equal to end_time"),
        }
    }

    list_observations.assert_not_called()


def test_equal_start_and_end_times_are_accepted() -> None:
    client = _client()

    timestamp = "2026-08-24T12:00:00Z"

    with patch(
        "app.api.routes.observations.list_observations",
        return_value=[],
    ) as list_observations:
        response = client.get(
            "/api/v1/observations",
            params={
                "start_time": timestamp,
                "end_time": timestamp,
            },
        )

    assert response.status_code == 200
    list_observations.assert_called_once()


def test_validation_error_contains_code_message_and_details() -> None:
    client = _client()

    response = client.get(
        "/api/v1/solar-conditions",
        params={
            "limit": 0,
        },
    )

    assert response.status_code == 422

    error = response.json()["error"]

    assert set(error) == {
        "code",
        "message",
        "details",
    }

    assert error["code"] == "validation_error"
    assert error["message"] == "Request validation failed"
    assert isinstance(error["details"], list)
    assert error["details"]


def test_observations_response_validation_rejects_malformed_output() -> None:
    client = _client(
        raise_server_exceptions=False,
    )

    with patch(
        "app.api.routes.observations.list_observations",
        return_value=[object()],
    ):
        response = client.get(
            "/api/v1/observations",
        )

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "response_validation_error",
            "message": "Response validation failed",
        }
    }


def test_solar_response_validation_rejects_malformed_output() -> None:
    client = _client(
        raise_server_exceptions=False,
    )

    with patch(
        "app.api.routes.solar_conditions.list_solar_conditions",
        return_value=[object()],
    ):
        response = client.get(
            "/api/v1/solar-conditions",
        )

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "response_validation_error",
            "message": "Response validation failed",
        }
    }


def test_station_response_validation_rejects_malformed_output() -> None:
    client = _client(
        raise_server_exceptions=False,
    )

    with patch(
        "app.api.routes.stations.list_stations",
        return_value=[object()],
    ):
        response = client.get(
            "/api/v1/stations",
        )

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "response_validation_error",
            "message": "Response validation failed",
        }
    }


def test_existing_api_error_uses_standard_error_envelope() -> None:
    app: FastAPI = create_app()

    @app.get("/test-api-error")
    async def test_api_error() -> None:
        raise APIError(
            status_code=403,
            code="forbidden",
            message="Access denied",
        )

    client = TestClient(app)

    response = client.get(
        "/test-api-error",
    )

    assert response.status_code == 403
    assert response.json() == {
        "error": {
            "code": "forbidden",
            "message": "Access denied",
        }
    }
