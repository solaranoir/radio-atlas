from datetime import UTC, datetime

from app.domain import SolarObservation, SpotObservation, StationObservation
from app.observations.deduplication import ObservationDeduplicator


def test_same_psk_sequence_is_duplicate() -> None:
    deduplicator = ObservationDeduplicator()

    first = SpotObservation(
        provider="psk_reporter",
        observed_at=datetime(2026, 8, 21, 12, 0, tzinfo=UTC),
        sequence_number=100,
        sender_callsign="EA5JLN",
        receiver_callsign="DL4JC",
        mode="FT8",
    )

    second = first.model_copy()

    assert deduplicator.is_duplicate(first) is False
    assert deduplicator.is_duplicate(second) is True


def test_different_psk_sequence_is_not_duplicate() -> None:
    deduplicator = ObservationDeduplicator()

    first = SpotObservation(
        provider="psk_reporter",
        observed_at=datetime(2026, 8, 21, 12, 0, tzinfo=UTC),
        sequence_number=100,
        sender_callsign="EA5JLN",
        receiver_callsign="DL4JC",
        mode="FT8",
    )

    second = first.model_copy(update={"sequence_number": 101})

    assert deduplicator.is_duplicate(first) is False
    assert deduplicator.is_duplicate(second) is False


def test_spot_without_sequence_uses_composite_key() -> None:
    deduplicator = ObservationDeduplicator()

    first = SpotObservation(
        provider="psk_reporter",
        observed_at=datetime(2026, 8, 21, 12, 0, tzinfo=UTC),
        sender_callsign="EA5JLN",
        receiver_callsign="DL4JC",
        frequency_hz=14_075_361,
        mode="FT8",
    )

    second = first.model_copy()

    assert deduplicator.is_duplicate(first) is False
    assert deduplicator.is_duplicate(second) is True


def test_same_solar_type_and_timestamp_is_duplicate() -> None:
    deduplicator = ObservationDeduplicator()

    first = SolarObservation(
        provider="noaa",
        observed_at=datetime(2026, 8, 21, 12, 0, tzinfo=UTC),
        observation_type="kp_index",
        value=2.0,
        unit="kp",
    )

    second = first.model_copy()

    assert deduplicator.is_duplicate(first) is False
    assert deduplicator.is_duplicate(second) is True


def test_different_solar_type_same_timestamp_is_not_duplicate() -> None:
    deduplicator = ObservationDeduplicator()

    first = SolarObservation(
        provider="noaa",
        observed_at=datetime(2026, 8, 21, 12, 0, tzinfo=UTC),
        observation_type="kp_index",
        value=2.0,
        unit="kp",
    )

    second = SolarObservation(
        provider="noaa",
        observed_at=first.observed_at,
        observation_type="sunspot_number",
        value=66,
        unit="count",
    )

    assert deduplicator.is_duplicate(first) is False
    assert deduplicator.is_duplicate(second) is False


def test_same_station_at_different_times_is_not_duplicate() -> None:
    deduplicator = ObservationDeduplicator()

    first = StationObservation(
        provider="psk_reporter",
        observed_at=datetime(2026, 8, 21, 12, 0, tzinfo=UTC),
        callsign="EA5JLN",
    )

    second = first.model_copy(
        update={
            "observed_at": datetime(
                2026,
                8,
                21,
                12,
                5,
                tzinfo=UTC,
            )
        }
    )

    assert deduplicator.is_duplicate(first) is False
    assert deduplicator.is_duplicate(second) is False


def test_psk_duplicate_ignores_changed_payload_when_sequence_matches() -> None:
    deduplicator = ObservationDeduplicator()

    first = SpotObservation(
        provider="psk_reporter",
        observed_at=datetime(2026, 8, 21, 12, 0, tzinfo=UTC),
        sequence_number=100,
        sender_callsign="EA5JLN",
        receiver_callsign="DL4JC",
        mode="FT8",
        snr_db=-5,
    )

    second = first.model_copy(update={"snr_db": -12})

    assert deduplicator.is_duplicate(first) is False
    assert deduplicator.is_duplicate(second) is True


def test_spot_without_sequence_at_different_time_is_not_duplicate() -> None:
    deduplicator = ObservationDeduplicator()

    first = SpotObservation(
        provider="psk_reporter",
        observed_at=datetime(2026, 8, 21, 12, 0, tzinfo=UTC),
        sender_callsign="EA5JLN",
        receiver_callsign="DL4JC",
        frequency_hz=14_075_361,
        mode="FT8",
    )

    second = first.model_copy(
        update={
            "observed_at": datetime(
                2026,
                8,
                21,
                12,
                1,
                tzinfo=UTC,
            )
        }
    )

    assert deduplicator.is_duplicate(first) is False
    assert deduplicator.is_duplicate(second) is False
