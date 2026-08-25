from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.domain import Observation, SolarObservation, SpotObservation
from app.infrastructure.database.models import (
    Provider,
    SolarCondition,
    Spot,
)


class ObservationPersistenceError(Exception):
    """Raised when an observation cannot be persisted."""


def get_provider_id(
    session: Session,
    provider_name: str,
) -> int:
    provider_id = session.scalar(
        select(Provider.id).where(
            Provider.name == provider_name,
        )
    )

    if provider_id is None:
        raise ObservationPersistenceError(f"Unknown provider: {provider_name}")

    return provider_id


def persist_observation(
    session: Session,
    observation: Observation,
) -> None:
    if isinstance(observation, SpotObservation):
        _persist_spot(session, observation)
        return

    if isinstance(observation, SolarObservation):
        _persist_solar_condition(session, observation)
        return

    raise ObservationPersistenceError(f"Unsupported observation type: {type(observation).__name__}")


def _persist_solar_condition(
    session: Session,
    observation: SolarObservation,
) -> None:
    provider_id = get_provider_id(
        session,
        observation.provider,
    )

    statement = (
        insert(SolarCondition)
        .values(
            provider_id=provider_id,
            observation_type=observation.observation_type,
            observed_at=observation.observed_at,
            value=observation.value,
            unit=observation.unit,
            data=observation.data,
        )
        .on_conflict_do_nothing(
            index_elements=[
                "provider_id",
                "observation_type",
                "observed_at",
            ],
        )
    )

    session.execute(statement)


def _persist_spot(
    session: Session,
    observation: SpotObservation,
) -> None:
    provider_id = get_provider_id(
        session,
        observation.provider,
    )

    model = Spot(
        provider_id=provider_id,
        sequence_number=observation.sequence_number,
        sender_callsign=observation.sender_callsign,
        receiver_callsign=observation.receiver_callsign,
        sender_grid=observation.sender_grid,
        receiver_grid=observation.receiver_grid,
        frequency_hz=observation.frequency_hz,
        band=observation.band,
        mode=observation.mode,
        snr_db=observation.snr_db,
        observed_at=observation.observed_at,
        transmitted_at=observation.transmitted_at,
        sender_entity_id=observation.sender_entity_id,
        receiver_entity_id=observation.receiver_entity_id,
    )

    session.add(model)


def ensure_providers(
    session: Session,
) -> None:
    providers = (
        (
            "noaa",
            "NOAA Space Weather Prediction Center",
            "solar",
        ),
        (
            "psk_reporter",
            "PSK Reporter",
            "spot",
        ),
    )

    for name, display_name, provider_type in providers:
        existing = session.scalar(
            select(Provider).where(
                Provider.name == name,
            )
        )

        if existing is not None:
            continue

        session.add(
            Provider(
                name=name,
                display_name=display_name,
                provider_type=provider_type,
            )
        )
