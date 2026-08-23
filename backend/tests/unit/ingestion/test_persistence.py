from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from app.domain import (
    SolarObservation,
    SpotObservation,
    StationObservation,
)
from app.infrastructure.database.models import (
    Provider,
    SolarCondition,
    Spot,
)
from app.ingestion.persistence import (
    ObservationPersistenceError,
    ensure_providers,
    get_provider_id,
    persist_observation,
)


def test_get_provider_id_finds_known_provider() -> None:
    session = MagicMock(spec=Session)
    session.scalar.return_value = 42

    provider_id = get_provider_id(
        session,
        "noaa",
    )

    assert provider_id == 42
    session.scalar.assert_called_once()


def test_get_provider_id_rejects_unknown_provider() -> None:
    session = MagicMock(spec=Session)
    session.scalar.return_value = None

    with pytest.raises(
        ObservationPersistenceError,
        match="Unknown provider: missing_provider",
    ):
        get_provider_id(
            session,
            "missing_provider",
        )


def test_ensure_providers_creates_noaa_and_psk_reporter() -> None:
    session = MagicMock(spec=Session)

    # Neither provider exists yet.
    session.scalar.side_effect = [
        None,
        None,
    ]

    ensure_providers(session)

    assert session.add.call_count == 2

    added = [call.args[0] for call in session.add.call_args_list]

    assert all(isinstance(provider, Provider) for provider in added)

    providers_by_name = {provider.name: provider for provider in added}

    assert set(providers_by_name) == {
        "noaa",
        "psk_reporter",
    }

    assert providers_by_name["noaa"].display_name == "NOAA Space Weather Prediction Center"
    assert providers_by_name["noaa"].provider_type == "solar"

    assert providers_by_name["psk_reporter"].display_name == "PSK Reporter"
    assert providers_by_name["psk_reporter"].provider_type == "spot"


def test_ensure_providers_is_idempotent() -> None:
    session = MagicMock(spec=Session)

    session.scalar.side_effect = [
        Provider(
            name="noaa",
            display_name="NOAA Space Weather Prediction Center",
            provider_type="solar",
        ),
        Provider(
            name="psk_reporter",
            display_name="PSK Reporter",
            provider_type="spot",
        ),
    ]

    ensure_providers(session)

    session.add.assert_not_called()


def test_persist_observation_creates_solar_condition() -> None:
    session = MagicMock(spec=Session)

    # get_provider_id()
    session.scalar.return_value = 7

    observation = SolarObservation(
        provider="noaa",
        observed_at=datetime(
            2026,
            8,
            20,
            12,
            0,
            tzinfo=UTC,
        ),
        observation_type="kp_index",
        value=2.0,
        unit="kp",
        data={
            "estimated_kp": 1.67,
            "category": "1M",
        },
    )

    persist_observation(
        session,
        observation,
    )

    session.add.assert_called_once()

    model = session.add.call_args.args[0]

    assert isinstance(model, SolarCondition)
    assert model.provider_id == 7
    assert model.observation_type == "kp_index"
    assert model.value == 2.0
    assert model.unit == "kp"
    assert model.observed_at == observation.observed_at
    assert model.data == observation.data


def test_persist_observation_creates_spot() -> None:
    session = MagicMock(spec=Session)

    # get_provider_id()
    session.scalar.return_value = 11

    observation = SpotObservation(
        provider="psk_reporter",
        observed_at=datetime(
            2026,
            8,
            20,
            20,
            35,
            44,
            tzinfo=UTC,
        ),
        sequence_number=71899472730,
        sender_callsign="KO1L",
        receiver_callsign="SP8TN",
        sender_grid="FN32KQ63",
        receiver_grid="KO00RI",
        frequency_hz=14_076_358,
        band="20m",
        mode="FT8",
        snr_db=-16,
        transmitted_at=datetime(
            2026,
            8,
            20,
            20,
            35,
            44,
            tzinfo=UTC,
        ),
        sender_entity_id=291,
        receiver_entity_id=269,
    )

    persist_observation(
        session,
        observation,
    )

    session.add.assert_called_once()

    model = session.add.call_args.args[0]

    assert isinstance(model, Spot)
    assert model.provider_id == 11
    assert model.sequence_number == 71899472730
    assert model.sender_callsign == "KO1L"
    assert model.receiver_callsign == "SP8TN"
    assert model.sender_grid == "FN32KQ63"
    assert model.receiver_grid == "KO00RI"
    assert model.frequency_hz == 14_076_358
    assert model.band == "20m"
    assert model.mode == "FT8"
    assert model.snr_db == -16
    assert model.sender_entity_id == 291
    assert model.receiver_entity_id == 269


def test_persist_observation_rejects_unsupported_type() -> None:
    session = MagicMock(spec=Session)

    observation = StationObservation(
        provider="test",
        observed_at=datetime(
            2026,
            8,
            20,
            12,
            0,
            tzinfo=UTC,
        ),
        callsign="KK7QEA",
    )

    with pytest.raises(
        ObservationPersistenceError,
        match="Unsupported observation type: StationObservation",
    ):
        persist_observation(
            session,
            observation,
        )

    session.add.assert_not_called()
