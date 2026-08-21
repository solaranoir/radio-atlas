from collections.abc import Hashable

from app.domain import (
    Observation,
    SolarObservation,
    SpotObservation,
    StationObservation,
)


def observation_key(
    observation: Observation,
) -> Hashable:
    if isinstance(observation, SpotObservation):
        if observation.sequence_number is not None:
            return (
                "spot",
                observation.provider,
                observation.sequence_number,
            )

        return (
            "spot",
            observation.provider,
            observation.observed_at,
            observation.sender_callsign,
            observation.receiver_callsign,
            observation.frequency_hz,
            observation.mode,
        )

    if isinstance(observation, SolarObservation):
        return (
            "solar",
            observation.provider,
            observation.observation_type,
            observation.observed_at,
        )

    if isinstance(observation, StationObservation):
        return (
            "station",
            observation.provider,
            observation.callsign,
            observation.observed_at,
        )

    return (
        observation.__class__.__name__,
        observation.provider,
        observation.observed_at,
    )


class ObservationDeduplicator:
    def __init__(self) -> None:
        self._seen: set[Hashable] = set()

    def is_duplicate(
        self,
        observation: Observation,
    ) -> bool:
        key = observation_key(observation)

        if key in self._seen:
            return True

        self._seen.add(key)
        return False
