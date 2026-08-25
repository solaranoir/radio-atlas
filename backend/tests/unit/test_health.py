from datetime import UTC, datetime

from app.health import HealthStatus, ProviderHealth


def test_provider_begins_as_unknown() -> None:
    health = ProviderHealth(
        provider="noaa",
    )

    assert health.provider == "noaa"
    assert health.status is HealthStatus.UNKNOWN
    assert health.last_success_at is None
    assert health.last_failure_at is None
    assert health.last_error is None


def test_success_sets_status_to_healthy() -> None:
    health = ProviderHealth(
        provider="noaa",
    )

    health.record_success()

    assert health.status is HealthStatus.HEALTHY


def test_success_records_last_success_at() -> None:
    health = ProviderHealth(
        provider="noaa",
    )

    before = datetime.now(UTC)

    health.record_success()

    after = datetime.now(UTC)

    assert health.last_success_at is not None
    assert before <= health.last_success_at <= after


def test_failure_sets_status_to_unhealthy() -> None:
    health = ProviderHealth(
        provider="noaa",
    )

    health.record_failure(
        RuntimeError("provider failed"),
    )

    assert health.status is HealthStatus.UNHEALTHY


def test_failure_records_last_failure_at() -> None:
    health = ProviderHealth(
        provider="noaa",
    )

    before = datetime.now(UTC)

    health.record_failure(
        RuntimeError("provider failed"),
    )

    after = datetime.now(UTC)

    assert health.last_failure_at is not None
    assert before <= health.last_failure_at <= after


def test_failure_stores_error_message() -> None:
    health = ProviderHealth(
        provider="psk_reporter",
    )

    health.record_failure(
        RuntimeError("MQTT connection lost"),
    )

    assert health.last_error == "MQTT connection lost"


def test_later_success_clears_last_error() -> None:
    health = ProviderHealth(
        provider="psk_reporter",
    )

    health.record_failure(
        RuntimeError("MQTT connection lost"),
    )

    assert health.last_error == "MQTT connection lost"

    health.record_success()

    assert health.status is HealthStatus.HEALTHY
    assert health.last_error is None
