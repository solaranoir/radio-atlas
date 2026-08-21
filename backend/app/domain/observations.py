import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

GRID_SQUARE_PATTERN = re.compile(r"^[A-R]{2}[0-9]{2}([A-X]{2})?([0-9]{2})?([A-X]{2})?$")


def _validate_grid_square(
    value: str | None,
) -> str | None:
    if value is None:
        return None

    normalized = value.strip().upper()

    if not normalized:
        raise ValueError("grid square must not be empty")

    if not GRID_SQUARE_PATTERN.fullmatch(normalized):
        raise ValueError("invalid Maidenhead grid square")

    return normalized


def _validate_callsign(value: str) -> str:
    normalized = value.strip().upper()

    if not normalized:
        raise ValueError("callsign must not be empty")

    if len(normalized) > 32:
        raise ValueError("callsign is too long")

    if not all(character.isalnum() or character == "/" for character in normalized):
        raise ValueError("callsign contains invalid characters")

    return normalized


def _validate_band(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip().lower()

    if not normalized:
        raise ValueError("band must not be empty")

    return normalized


class ObservationBase(BaseModel):
    provider: str
    observed_at: datetime

    @field_validator("observed_at")
    @classmethod
    def validate_observed_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")

        return value


class SolarObservation(ObservationBase):
    observation_type: Literal[
        "solar_flux",
        "kp_index",
        "sunspot_number",
        "aurora",
        "magnetic_field",
        "solar_wind",
    ]

    value: float | int | None = None
    unit: str | None = None
    data: dict[str, object] = Field(default_factory=dict)


class SpotObservation(ObservationBase):
    sequence_number: int | None = None

    sender_callsign: str
    receiver_callsign: str

    sender_grid: str | None = None
    receiver_grid: str | None = None

    frequency_hz: int | None = Field(default=None, gt=0)
    band: str | None = None
    mode: str

    snr_db: int | None = None

    transmitted_at: datetime | None = None

    sender_entity_id: int | None = None
    receiver_entity_id: int | None = None

    @field_validator("transmitted_at")
    @classmethod
    def validate_transmitted_at(
        cls,
        value: datetime | None,
    ) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("transmitted_at must be timezone-aware")

        return value

    @field_validator(
        "sender_callsign",
        "receiver_callsign",
    )
    @classmethod
    def validate_callsign(cls, value: str) -> str:
        return _validate_callsign(value)

    @field_validator("band")
    @classmethod
    def validate_band(
        cls,
        value: str | None,
    ) -> str | None:
        return _validate_band(value)

    @field_validator(
        "sender_grid",
        "receiver_grid",
    )
    @classmethod
    def validate_grid_square(
        cls,
        value: str | None,
    ) -> str | None:
        return _validate_grid_square(value)


class StationObservation(ObservationBase):
    callsign: str
    grid_square: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    entity_id: int | None = None

    @field_validator(
        "callsign",
    )
    @classmethod
    def validate_callsign(cls, value: str) -> str:
        return _validate_callsign(value)

    @field_validator("grid_square")
    @classmethod
    def validate_grid_square(
        cls,
        value: str | None,
    ) -> str | None:
        return _validate_grid_square(value)


class PropagationObservation(ObservationBase):
    source_grid: str | None = None
    destination_grid: str | None = None

    frequency_hz: int | None = Field(default=None, gt=0)
    band: str | None = None
    mode: str | None = None

    signal_report_db: int | None = None
    distance_km: float | None = Field(default=None, ge=0)

    data: dict[str, object] = Field(default_factory=dict)

    @field_validator("band")
    @classmethod
    def validate_band(
        cls,
        value: str | None,
    ) -> str | None:
        return _validate_band(value)

    @field_validator(
        "source_grid",
        "destination_grid",
    )
    @classmethod
    def validate_grid_square(
        cls,
        value: str | None,
    ) -> str | None:
        return _validate_grid_square(value)


Observation = PropagationObservation | SolarObservation | SpotObservation | StationObservation
