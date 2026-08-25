from datetime import UTC, datetime

from pydantic import BaseModel, Field, field_validator


class Callsign(BaseModel):
    value: str

    @field_validator("value")
    @classmethod
    def normalize_callsign(cls, value: str) -> str:
        normalized = value.strip().upper()

        if "-" in normalized:
            base, suffix = normalized.rsplit("-", maxsplit=1)

            if suffix.isdigit() and 0 <= int(suffix) <= 15:
                normalized = base

        if not normalized:
            raise ValueError("callsign must not be empty")

        return normalized


class Frequency(BaseModel):
    hz: int = Field(gt=0)

    @property
    def mhz(self) -> float:
        return self.hz / 1_000_000


class Band(BaseModel):
    value: str

    @field_validator("value")
    @classmethod
    def normalize_band(cls, value: str) -> str:
        normalized = value.strip().lower()

        if not normalized:
            raise ValueError("band must not be empty")

        return normalized


class OperatingMode(BaseModel):
    value: str

    @field_validator("value")
    @classmethod
    def normalize_mode(cls, value: str) -> str:
        normalized = value.strip().upper()

        if not normalized:
            raise ValueError("mode must not be empty")

        return normalized


class GridSquare(BaseModel):
    value: str

    @field_validator("value")
    @classmethod
    def normalize_grid_square(cls, value: str) -> str:
        normalized = value.strip().upper()

        if not normalized:
            raise ValueError("grid square must not be empty")

        if len(normalized) < 4:
            raise ValueError("grid square must contain at least 4 characters")

        if len(normalized) % 2 != 0:
            raise ValueError("grid square must contain an even number of characters")

        return normalized


class Coordinate(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class NormalizedPSKSpot(BaseModel):
    sequence_number: int
    sender_callsign: Callsign
    receiver_callsign: Callsign
    sender_grid: GridSquare | None = None
    receiver_grid: GridSquare | None = None
    frequency: Frequency | None = None
    band: Band | None = None
    mode: OperatingMode
    observed_at: datetime
    transmitted_at: datetime | None = None
    snr_db: int | None = None
    sender_entity_id: int | None = None
    receiver_entity_id: int | None = None


class PSKReporterSpot(BaseModel):
    sequence_number: int = Field(gt=0)
    frequency_hz: int | None = Field(default=None, gt=0)
    mode: str
    snr_db: int | None = None
    observed_at: int
    transmitted_at: int | None = None
    sender_callsign: str
    sender_locator: str | None = None
    receiver_callsign: str
    receiver_locator: str | None = None
    sender_entity_id: int | None = None
    receiver_entity_id: int | None = None
    band: str | None = None

    @classmethod
    def from_mqtt_payload(
        cls,
        payload: dict[str, object],
    ) -> "PSKReporterSpot":
        return cls(
            sequence_number=payload["sq"],
            frequency_hz=payload.get("f"),
            mode=payload["md"],
            snr_db=payload.get("rp"),
            observed_at=payload["t"],
            transmitted_at=payload.get("t_tx"),
            sender_callsign=payload["sc"],
            sender_locator=payload.get("sl"),
            receiver_callsign=payload["rc"],
            receiver_locator=payload.get("rl"),
            sender_entity_id=payload.get("sa"),
            receiver_entity_id=payload.get("ra"),
            band=payload.get("b"),
        )

    def normalize(self) -> NormalizedPSKSpot:
        return NormalizedPSKSpot(
            sequence_number=self.sequence_number,
            sender_callsign=Callsign(value=self.sender_callsign),
            receiver_callsign=Callsign(value=self.receiver_callsign),
            sender_grid=(
                GridSquare(value=self.sender_locator) if self.sender_locator is not None else None
            ),
            receiver_grid=(
                GridSquare(value=self.receiver_locator)
                if self.receiver_locator is not None
                else None
            ),
            frequency=(Frequency(hz=self.frequency_hz) if self.frequency_hz is not None else None),
            band=(Band(value=self.band) if self.band is not None else None),
            mode=OperatingMode(value=self.mode),
            observed_at=datetime.fromtimestamp(
                self.observed_at,
                tz=UTC,
            ),
            transmitted_at=(
                datetime.fromtimestamp(
                    self.transmitted_at,
                    tz=UTC,
                )
                if self.transmitted_at is not None
                else None
            ),
            snr_db=self.snr_db,
            sender_entity_id=self.sender_entity_id,
            receiver_entity_id=self.receiver_entity_id,
        )
