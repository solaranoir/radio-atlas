from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ObservationBase(BaseModel):
    provider: str
    observed_at: datetime


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


class StationObservation(ObservationBase):
    callsign: str
    grid_square: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    entity_id: int | None = None


class PropagationObservation(ObservationBase):
    source_grid: str | None = None
    destination_grid: str | None = None

    frequency_hz: int | None = Field(default=None, gt=0)
    band: str | None = None
    mode: str | None = None

    signal_report_db: int | None = None
    distance_km: float | None = Field(default=None, ge=0)

    data: dict[str, object] = Field(default_factory=dict)


Observation = PropagationObservation | SolarObservation | SpotObservation | StationObservation
