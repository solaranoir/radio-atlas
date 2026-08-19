from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SolarFlux(BaseModel):
    """Normalized NOAA F10.7 solar flux observation."""

    model_config = ConfigDict(frozen=True)

    observed_at: datetime
    frequency_mhz: int = Field(gt=0)
    flux_sfu: float = Field(ge=0)
    reporting_schedule: str
    ninety_day_mean: float | None = Field(default=None, ge=0)

class KpIndex(BaseModel):
    """Normalized planetary K-index observation."""

    model_config = ConfigDict(frozen=True)

    observed_at: datetime
    kp_index: float = Field(ge=0)
    estimated_kp: float = Field(ge=0)
    category: str


class SunspotNumber(BaseModel):
    """Normalized NOAA sunspot observation."""

    model_config = ConfigDict(frozen=True)

    observed_at: datetime
    sunspot_number: int = Field(ge=0)


class AuroraGridCell(BaseModel):
    """Single geographic cell in an OVATION aurora forecast."""

    model_config = ConfigDict(frozen=True)

    longitude: float = Field(ge=-180, le=360)
    latitude: float = Field(ge=-90, le=90)
    aurora: int = Field(ge=0)


class AuroraForecast(BaseModel):
    """Normalized NOAA OVATION aurora forecast."""

    model_config = ConfigDict(frozen=True)

    observed_at: datetime
    forecast_at: datetime
    cells: list[AuroraGridCell]


class SolarMagneticField(BaseModel):
    """Normalized interplanetary magnetic-field observation."""

    model_config = ConfigDict(frozen=True)

    observed_at: datetime
    total_field_nt: float
    bz_gsm_nt: float
    data_quality: int


class SolarWind(BaseModel):
    """Normalized solar-wind plasma observation."""

    model_config = ConfigDict(frozen=True)

    observed_at: datetime
    proton_speed_kms: float = Field(ge=0)
    proton_density_cm3: float = Field(ge=0)
    proton_temperature_k: float = Field(ge=0)
    data_quality: int
