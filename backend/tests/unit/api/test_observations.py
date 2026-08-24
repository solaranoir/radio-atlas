from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.infrastructure.database.models import Spot
from app.main import create_app


def _client() -> TestClient:
    return TestClient(create_app())


def test_get_observations_returns_200() -> None:
    client = _client()

    with patch(
        "app.api.routes.observations.list_observations",
        return_value=[],
    ):
        response = client.get("/api/v1/observations")

    assert response.status_code == 200
    assert response.json() == []


def test_default_query_uses_default_limit_and_offset() -> None:
    client = _client()

    with patch(
        "app.api.routes.observations.list_observations",
        return_value=[],
    ) as list_observations:
        response = client.get("/api/v1/observations")

    assert response.status_code == 200

    call = list_observations.call_args

    assert call is not None
    assert call.kwargs["limit"] == 100
    assert call.kwargs["offset"] == 0
    assert call.kwargs["start_time"] is None
    assert call.kwargs["end_time"] is None
    assert call.kwargs["band"] is None


def test_start_time_is_parsed_and_forwarded() -> None:
    client = _client()

    with patch(
        "app.api.routes.observations.list_observations",
        return_value=[],
    ) as list_observations:
        response = client.get(
            "/api/v1/observations",
            params={
                "start_time": "2026-08-20T12:00:00Z",
            },
        )

    assert response.status_code == 200

    call = list_observations.call_args

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
        "app.api.routes.observations.list_observations",
        return_value=[],
    ) as list_observations:
        response = client.get(
            "/api/v1/observations",
            params={
                "end_time": "2026-08-21T12:00:00Z",
            },
        )

    assert response.status_code == 200

    call = list_observations.call_args

    assert call is not None
    assert call.kwargs["end_time"] == datetime(
        2026,
        8,
        21,
        12,
        0,
        tzinfo=UTC,
    )


def test_band_is_forwarded() -> None:
    client = _client()

    with patch(
        "app.api.routes.observations.list_observations",
        return_value=[],
    ) as list_observations:
        response = client.get(
            "/api/v1/observations",
            params={
                "band": "20m",
            },
        )

    assert response.status_code == 200

    call = list_observations.call_args

    assert call is not None
    assert call.kwargs["band"] == "20m"


def test_custom_limit_and_offset_are_forwarded() -> None:
    client = _client()

    with patch(
        "app.api.routes.observations.list_observations",
        return_value=[],
    ) as list_observations:
        response = client.get(
            "/api/v1/observations",
            params={
                "limit": 25,
                "offset": 50,
            },
        )

    assert response.status_code == 200

    call = list_observations.call_args

    assert call is not None
    assert call.kwargs["limit"] == 25
    assert call.kwargs["offset"] == 50


def test_invalid_zero_limit_returns_422() -> None:
    client = _client()

    response = client.get(
        "/api/v1/observations",
        params={
            "limit": 0,
        },
    )

    assert response.status_code == 422


def test_invalid_limit_above_max_returns_422() -> None:
    client = _client()

    response = client.get(
        "/api/v1/observations",
        params={
            "limit": 501,
        },
    )

    assert response.status_code == 422


def test_negative_offset_returns_422() -> None:
    client = _client()

    response = client.get(
        "/api/v1/observations",
        params={
            "offset": -1,
        },
    )

    assert response.status_code == 422


def test_spot_rows_serialize_into_response_model() -> None:
    client = _client()

    observed_at = datetime(
        2026,
        8,
        20,
        20,
        35,
        44,
        tzinfo=UTC,
    )

    transmitted_at = datetime(
        2026,
        8,
        20,
        20,
        35,
        29,
        tzinfo=UTC,
    )

    spot = MagicMock(spec=Spot)

    spot.id = 42
    spot.provider_id = 2
    spot.sequence_number = 71899472730
    spot.sender_callsign = "EA5JLN"
    spot.receiver_callsign = "DL4JC"
    spot.sender_grid = "IM99TN"
    spot.receiver_grid = "JN39LH"
    spot.frequency_hz = 14_075_361
    spot.band = "20m"
    spot.mode = "FT8"
    spot.snr_db = -5
    spot.observed_at = observed_at
    spot.transmitted_at = transmitted_at

    with patch(
        "app.api.routes.observations.list_observations",
        return_value=[spot],
    ):
        response = client.get("/api/v1/observations")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 42,
            "provider_id": 2,
            "sequence_number": 71899472730,
            "sender_callsign": "EA5JLN",
            "receiver_callsign": "DL4JC",
            "sender_grid": "IM99TN",
            "receiver_grid": "JN39LH",
            "frequency_hz": 14_075_361,
            "band": "20m",
            "mode": "FT8",
            "snr_db": -5,
            "observed_at": "2026-08-20T20:35:44Z",
            "transmitted_at": "2026-08-20T20:35:29Z",
        }
    ]
