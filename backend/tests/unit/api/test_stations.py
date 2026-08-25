from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.infrastructure.database.models import Station
from app.main import create_app


def _client() -> TestClient:
    return TestClient(create_app())


def test_get_stations_returns_200() -> None:
    client = _client()

    with patch(
        "app.api.routes.stations.list_stations",
        return_value=[],
    ):
        response = client.get("/api/v1/stations")

    assert response.status_code == 200
    assert response.json() == []


def test_default_query_uses_default_limit_and_offset() -> None:
    client = _client()

    with patch(
        "app.api.routes.stations.list_stations",
        return_value=[],
    ) as list_stations:
        response = client.get("/api/v1/stations")

    assert response.status_code == 200

    call = list_stations.call_args

    assert call is not None
    assert call.kwargs["limit"] == 100
    assert call.kwargs["offset"] == 0
    assert call.kwargs["callsign"] is None


def test_callsign_is_forwarded() -> None:
    client = _client()

    with patch(
        "app.api.routes.stations.list_stations",
        return_value=[],
    ) as list_stations:
        response = client.get(
            "/api/v1/stations",
            params={
                "callsign": "KK7QEA",
            },
        )

    assert response.status_code == 200

    call = list_stations.call_args

    assert call is not None
    assert call.kwargs["callsign"] == "KK7QEA"


def test_lowercase_callsign_is_forwarded_to_repository() -> None:
    client = _client()

    with patch(
        "app.api.routes.stations.list_stations",
        return_value=[],
    ) as list_stations:
        response = client.get(
            "/api/v1/stations",
            params={
                "callsign": "kk7qea",
            },
        )

    assert response.status_code == 200

    call = list_stations.call_args

    assert call is not None

    # The route forwards the caller's value. The repository is responsible
    # for normalizing it to uppercase before constructing the SQL query.
    assert call.kwargs["callsign"] == "kk7qea"


def test_custom_limit_and_offset_are_forwarded() -> None:
    client = _client()

    with patch(
        "app.api.routes.stations.list_stations",
        return_value=[],
    ) as list_stations:
        response = client.get(
            "/api/v1/stations",
            params={
                "limit": 25,
                "offset": 50,
            },
        )

    assert response.status_code == 200

    call = list_stations.call_args

    assert call is not None
    assert call.kwargs["limit"] == 25
    assert call.kwargs["offset"] == 50


def test_invalid_zero_limit_returns_422() -> None:
    client = _client()

    response = client.get(
        "/api/v1/stations",
        params={
            "limit": 0,
        },
    )

    assert response.status_code == 422


def test_invalid_limit_above_max_returns_422() -> None:
    client = _client()

    response = client.get(
        "/api/v1/stations",
        params={
            "limit": 501,
        },
    )

    assert response.status_code == 422


def test_negative_offset_returns_422() -> None:
    client = _client()

    response = client.get(
        "/api/v1/stations",
        params={
            "offset": -1,
        },
    )

    assert response.status_code == 422


def test_station_rows_serialize_into_response_model() -> None:
    client = _client()

    first_seen_at = datetime(
        2026,
        8,
        20,
        12,
        0,
        tzinfo=UTC,
    )

    last_seen_at = datetime(
        2026,
        8,
        24,
        17,
        30,
        tzinfo=UTC,
    )

    station = MagicMock(spec=Station)

    station.id = 42
    station.callsign = "KK7QEA"
    station.grid_square = "DM25"
    station.latitude = 36.0395
    station.longitude = -114.9817
    station.entity_id = 291
    station.first_seen_at = first_seen_at
    station.last_seen_at = last_seen_at

    with patch(
        "app.api.routes.stations.list_stations",
        return_value=[station],
    ):
        response = client.get("/api/v1/stations")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 42,
            "callsign": "KK7QEA",
            "grid_square": "DM25",
            "latitude": 36.0395,
            "longitude": -114.9817,
            "entity_id": 291,
            "first_seen_at": "2026-08-20T12:00:00Z",
            "last_seen_at": "2026-08-24T17:30:00Z",
        }
    ]
