from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.infrastructure.database.models import SolarCondition
from app.main import create_app


def _client() -> TestClient:
    return TestClient(create_app())


def test_get_solar_conditions_returns_200() -> None:
    client = _client()

    with patch(
        "app.api.routes.solar_conditions.list_solar_conditions",
        return_value=[],
    ):
        response = client.get("/api/v1/solar-conditions")

    assert response.status_code == 200
    assert response.json() == []


def test_default_query_uses_default_limit_and_offset() -> None:
    client = _client()

    with patch(
        "app.api.routes.solar_conditions.list_solar_conditions",
        return_value=[],
    ) as list_solar_conditions:
        response = client.get("/api/v1/solar-conditions")

    assert response.status_code == 200

    call = list_solar_conditions.call_args

    assert call is not None
    assert call.kwargs["limit"] == 100
    assert call.kwargs["offset"] == 0
    assert call.kwargs["observation_type"] is None
    assert call.kwargs["start_time"] is None
    assert call.kwargs["end_time"] is None


def test_observation_type_is_forwarded() -> None:
    client = _client()

    with patch(
        "app.api.routes.solar_conditions.list_solar_conditions",
        return_value=[],
    ) as list_solar_conditions:
        response = client.get(
            "/api/v1/solar-conditions",
            params={
                "observation_type": "kp_index",
            },
        )

    assert response.status_code == 200

    call = list_solar_conditions.call_args

    assert call is not None
    assert call.kwargs["observation_type"] == "kp_index"


def test_start_time_is_parsed_and_forwarded() -> None:
    client = _client()

    with patch(
        "app.api.routes.solar_conditions.list_solar_conditions",
        return_value=[],
    ) as list_solar_conditions:
        response = client.get(
            "/api/v1/solar-conditions",
            params={
                "start_time": "2026-08-20T12:00:00Z",
            },
        )

    assert response.status_code == 200

    call = list_solar_conditions.call_args

    assert call is not None
    assert call.kwargs["start_time"] == datetime(
        2026,
        8,
        20,
        12,
        0,
        tzinfo=UTC,
    )


def test_end_time_is_parsed_and_forwarded() -> None:
    client = _client()

    with patch(
        "app.api.routes.solar_conditions.list_solar_conditions",
        return_value=[],
    ) as list_solar_conditions:
        response = client.get(
            "/api/v1/solar-conditions",
            params={
                "end_time": "2026-08-21T12:00:00Z",
            },
        )

    assert response.status_code == 200

    call = list_solar_conditions.call_args

    assert call is not None
    assert call.kwargs["end_time"] == datetime(
        2026,
        8,
        21,
        12,
        0,
        tzinfo=UTC,
    )


def test_custom_limit_and_offset_are_forwarded() -> None:
    client = _client()

    with patch(
        "app.api.routes.solar_conditions.list_solar_conditions",
        return_value=[],
    ) as list_solar_conditions:
        response = client.get(
            "/api/v1/solar-conditions",
            params={
                "limit": 25,
                "offset": 50,
            },
        )

    assert response.status_code == 200

    call = list_solar_conditions.call_args

    assert call is not None
    assert call.kwargs["limit"] == 25
    assert call.kwargs["offset"] == 50


def test_invalid_zero_limit_returns_422() -> None:
    client = _client()

    response = client.get(
        "/api/v1/solar-conditions",
        params={
            "limit": 0,
        },
    )

    assert response.status_code == 422


def test_invalid_limit_above_max_returns_422() -> None:
    client = _client()

    response = client.get(
        "/api/v1/solar-conditions",
        params={
            "limit": 501,
        },
    )

    assert response.status_code == 422


def test_negative_offset_returns_422() -> None:
    client = _client()

    response = client.get(
        "/api/v1/solar-conditions",
        params={
            "offset": -1,
        },
    )

    assert response.status_code == 422


def test_solar_condition_rows_serialize_into_response_model() -> None:
    client = _client()

    observed_at = datetime(
        2026,
        8,
        20,
        12,
        0,
        tzinfo=UTC,
    )

    condition = MagicMock(spec=SolarCondition)

    condition.id = 17
    condition.provider_id = 1
    condition.observation_type = "solar_wind"
    condition.observed_at = observed_at
    condition.value = 432.5
    condition.unit = "km/s"
    condition.data = {
        "density": 6.2,
        "temperature": 118_000,
        "source": "ACE",
    }

    with patch(
        "app.api.routes.solar_conditions.list_solar_conditions",
        return_value=[condition],
    ):
        response = client.get("/api/v1/solar-conditions")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 17,
            "provider_id": 1,
            "observation_type": "solar_wind",
            "observed_at": "2026-08-20T12:00:00Z",
            "value": 432.5,
            "unit": "km/s",
            "data": {
                "density": 6.2,
                "temperature": 118000,
                "source": "ACE",
            },
        }
    ]
