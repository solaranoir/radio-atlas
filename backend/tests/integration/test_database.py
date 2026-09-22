from datetime import UTC, datetime

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain import (
    SolarObservation,
)
from app.infrastructure.database.models import (
    Provider,
    SolarCondition,
    Spot,
    Station,
)
from app.ingestion.persistence import persist_observation


def test_insert_provider(db_session: Session) -> None:
    provider = Provider(
        name="test_provider",
        display_name="Test Provider",
        provider_type="test",
    )

    db_session.add(provider)
    db_session.flush()

    assert provider.id is not None

    persisted = db_session.get(Provider, provider.id)

    assert persisted is not None
    assert persisted.name == "test_provider"
    assert persisted.display_name == "Test Provider"
    assert persisted.provider_type == "test"
    assert persisted.enabled is True


def test_update_provider(db_session: Session) -> None:
    provider = Provider(
        name="test_provider",
        display_name="Original Name",
        provider_type="test",
    )

    db_session.add(provider)
    db_session.flush()

    provider.display_name = "Updated Name"
    db_session.flush()

    db_session.expire(provider)

    assert provider.display_name == "Updated Name"


def test_delete_provider(db_session: Session) -> None:
    provider = Provider(
        name="test_provider",
        display_name="Test Provider",
        provider_type="test",
    )

    db_session.add(provider)
    db_session.flush()

    provider_id = provider.id

    db_session.delete(provider)
    db_session.flush()

    persisted = db_session.get(Provider, provider_id)

    assert persisted is None


def test_spot_relationships(db_session: Session) -> None:
    provider = Provider(
        name="test_psk_reporter",
        display_name="Test PSK Reporter",
        provider_type="spot",
    )

    sender = Station(callsign="EA5JLN")
    receiver = Station(callsign="DL4JC")

    db_session.add_all([provider, sender, receiver])
    db_session.flush()

    spot = Spot(
        provider_id=provider.id,
        sequence_number=123456,
        sender_station_id=sender.id,
        receiver_station_id=receiver.id,
        sender_callsign=sender.callsign,
        receiver_callsign=receiver.callsign,
        frequency_hz=14_075_361,
        band="20m",
        mode="FT8",
        observed_at=datetime(2026, 8, 20, 20, 35, 44, tzinfo=UTC),
    )

    db_session.add(spot)
    db_session.flush()

    assert spot.id is not None
    assert spot.provider_id == provider.id
    assert spot.sender_station_id == sender.id
    assert spot.receiver_station_id == receiver.id


def test_rejects_spot_with_unknown_provider(db_session: Session) -> None:
    spot = Spot(
        provider_id=999_999_999,
        sender_callsign="EA5JLN",
        receiver_callsign="DL4JC",
        frequency_hz=14_075_361,
        band="20m",
        mode="FT8",
        observed_at=datetime(2026, 8, 20, 20, 35, 44, tzinfo=UTC),
    )

    db_session.add(spot)

    with pytest.raises(IntegrityError):
        db_session.flush()


def test_rejects_duplicate_provider_name(db_session: Session) -> None:
    first = Provider(
        name="duplicate_provider",
        display_name="First Provider",
        provider_type="test",
    )
    second = Provider(
        name="duplicate_provider",
        display_name="Second Provider",
        provider_type="test",
    )

    db_session.add(first)
    db_session.flush()

    db_session.add(second)

    with pytest.raises(IntegrityError):
        db_session.flush()


def test_rejects_duplicate_station_callsign(db_session: Session) -> None:
    first = Station(callsign="KK7QEA")
    second = Station(callsign="KK7QEA")

    db_session.add(first)
    db_session.flush()

    db_session.add(second)

    with pytest.raises(IntegrityError):
        db_session.flush()


def test_rejects_duplicate_solar_observation(
    db_session: Session,
) -> None:
    provider = Provider(
        name="test_noaa",
        display_name="Test NOAA",
        provider_type="solar",
    )

    db_session.add(provider)
    db_session.flush()

    observed_at = datetime(2026, 8, 20, 12, 0, tzinfo=UTC)

    first = SolarCondition(
        provider_id=provider.id,
        observation_type="kp_index",
        observed_at=observed_at,
        value=2.0,
        unit="kp",
    )

    second = SolarCondition(
        provider_id=provider.id,
        observation_type="kp_index",
        observed_at=observed_at,
        value=3.0,
        unit="kp",
    )

    db_session.add(first)
    db_session.flush()

    db_session.add(second)

    with pytest.raises(IntegrityError):
        db_session.flush()


def test_rejects_duplicate_psk_sequence(
    db_session: Session,
) -> None:
    provider = Provider(
        name="test_psk",
        display_name="Test PSK Reporter",
        provider_type="spot",
    )

    db_session.add(provider)
    db_session.flush()

    first = Spot(
        provider_id=provider.id,
        sequence_number=123456,
        sender_callsign="EA5JLN",
        receiver_callsign="DL4JC",
        frequency_hz=14_075_361,
        band="20m",
        mode="FT8",
        observed_at=datetime(2026, 8, 20, 20, 35, 44, tzinfo=UTC),
    )

    second = Spot(
        provider_id=provider.id,
        sequence_number=123456,
        sender_callsign="W1AW",
        receiver_callsign="KK7QEA",
        frequency_hz=7_074_000,
        band="40m",
        mode="FT8",
        observed_at=datetime(2026, 8, 21, 1, 0, tzinfo=UTC),
    )

    db_session.add(first)
    db_session.flush()

    db_session.add(second)

    with pytest.raises(IntegrityError):
        db_session.flush()


def test_rejects_duplicate_sequence_less_spot_with_null_frequency(
    db_session: Session,
) -> None:
    provider = Provider(
        name="test_psk_null_frequency",
        display_name="Test PSK Reporter",
        provider_type="spot",
    )

    db_session.add(provider)
    db_session.flush()

    observed_at = datetime(2026, 8, 20, 20, 35, 44, tzinfo=UTC)

    first = Spot(
        provider_id=provider.id,
        sequence_number=None,
        sender_callsign="EA5JLN",
        receiver_callsign="DL4JC",
        frequency_hz=None,
        band="20m",
        mode="FT8",
        observed_at=observed_at,
    )

    second = Spot(
        provider_id=provider.id,
        sequence_number=None,
        sender_callsign="EA5JLN",
        receiver_callsign="DL4JC",
        frequency_hz=None,
        band="20m",
        mode="FT8",
        observed_at=observed_at,
    )

    db_session.add(first)
    db_session.flush()

    db_session.add(second)

    with pytest.raises(IntegrityError):
        db_session.flush()


def test_duplicate_solar_condition_is_ignored(
    db_session: Session,
) -> None:
    provider = Provider(
        name="test_noaa_duplicate_solar",
        display_name="Test NOAA Duplicate Solar",
        provider_type="solar",
    )

    db_session.add(provider)
    db_session.flush()

    observation = SolarObservation(
        provider="test_noaa_duplicate_solar",
        observed_at=datetime(
            2099,
            1,
            1,
            12,
            34,
            56,
            tzinfo=UTC,
        ),
        observation_type="solar_flux",
        value=132.0,
        unit="sfu",
        data={},
    )

    persist_observation(
        db_session,
        observation,
    )
    db_session.flush()

    persist_observation(
        db_session,
        observation,
    )
    db_session.flush()

    count = db_session.scalar(
        select(func.count())
        .select_from(SolarCondition)
        .where(
            SolarCondition.provider_id == provider.id,
            SolarCondition.observation_type == observation.observation_type,
            SolarCondition.observed_at == observation.observed_at,
        )
    )

    assert count == 1
