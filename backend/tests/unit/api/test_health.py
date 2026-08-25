from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.health import (
    HealthStatus,
    noaa_health,
    psk_reporter_health,
)
from app.main import create_app


def _client() -> TestClient:
    return TestClient(create_app())


def _reset_health() -> None:
    noaa_health.status = HealthStatus.UNKNOWN
    noaa_health.last_success_at = None
    noaa_health.last_failure_at = None
    noaa_health.last_error = None

    psk_reporter_health.status = HealthStatus.UNKNOWN
    psk_reporter_health.last_success_at = None
    psk_reporter_health.last_failure_at = None
    psk_reporter_health.last_error = None


def test_health_returns_200() -> None:
    _reset_health()
    client = _client()

    response = client.get("/health")

    assert response.status_code == 200


def test_health_is_unknown_when_provider_health_is_unknown() -> None:
    _reset_health()
    client = _client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "unknown"


def test_health_is_healthy_when_all_providers_are_healthy() -> None:
    _reset_health()

    noaa_health.record_success()
    psk_reporter_health.record_success()

    client = _client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_health_is_unhealthy_when_any_provider_is_unhealthy() -> None:
    _reset_health()

    noaa_health.record_success()
    psk_reporter_health.record_failure(
        RuntimeError("MQTT connection lost"),
    )

    client = _client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "unhealthy"


def test_health_lists_both_providers() -> None:
    _reset_health()
    client = _client()

    response = client.get("/health")

    providers = response.json()["providers"]

    assert {provider["provider"] for provider in providers} == {
        "noaa",
        "psk_reporter",
    }


def test_noaa_health_endpoint_returns_provider_health() -> None:
    _reset_health()

    noaa_health.record_success()

    client = _client()

    response = client.get("/health/noaa")

    assert response.status_code == 200

    body = response.json()

    assert body["provider"] == "noaa"
    assert body["status"] == "healthy"
    assert body["last_success_at"] is not None
    assert body["last_failure_at"] is None
    assert body["last_error"] is None


def test_psk_reporter_health_endpoint_returns_provider_health() -> None:
    _reset_health()

    psk_reporter_health.record_failure(
        RuntimeError("MQTT connection lost"),
    )

    client = _client()

    response = client.get("/health/psk-reporter")

    assert response.status_code == 200

    body = response.json()

    assert body["provider"] == "psk_reporter"
    assert body["status"] == "unhealthy"
    assert body["last_success_at"] is None
    assert body["last_failure_at"] is not None
    assert body["last_error"] == "MQTT connection lost"


def test_provider_health_timestamps_serialize_as_iso8601() -> None:
    _reset_health()

    noaa_health.status = HealthStatus.HEALTHY
    noaa_health.last_success_at = datetime(
        2026,
        8,
        24,
        20,
        0,
        tzinfo=UTC,
    )

    client = _client()

    response = client.get("/health/noaa")

    assert response.status_code == 200
    assert response.json()["last_success_at"] == "2026-08-24T20:00:00Z"
