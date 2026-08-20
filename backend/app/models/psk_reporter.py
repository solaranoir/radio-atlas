from pydantic import BaseModel, Field, field_validator


class Callsign(BaseModel):
    value: str

    @field_validator("value")
    @classmethod
    def normalize_callsign(cls, value: str) -> str:
        normalized = value.strip().upper()

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
