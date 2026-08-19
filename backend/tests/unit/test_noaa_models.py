from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.models.noaa import (
    AuroraForecast,
    AuroraGridCell,
    KpIndex,
    SolarFlux,
    SolarMagneticField,
    SolarWind,
    SunspotNumber,
)

# Tests for Solar Flux


def test_solar_flux_model() -> None:
    model = SolarFlux(
        observed_at=datetime(2026, 8, 15, 20, 0),
        frequency_mhz=2800,
        flux_sfu=117,
        reporting_schedule="Noon",
        ninety_day_mean=131,
    )

    assert model.frequency_mhz == 2800
    assert model.flux_sfu == 117


def test_solar_flux_rejects_negative_flux() -> None:
    with pytest.raises(ValidationError):
        SolarFlux(
            observed_at=datetime(2026, 8, 15),
            frequency_mhz=2800,
            flux_sfu=-1,
            reporting_schedule="Noon",
            ninety_day_mean=131,
        )


# Tests for Kp


def test_kp_index_model() -> None:
    model = KpIndex(
        observed_at=datetime(2026, 8, 15, 15, 58),
        kp_index=1,
        estimated_kp=0.67,
        category="1M",
    )

    assert model.kp_index == 1
    assert model.estimated_kp == 0.67
    assert model.category == "1M"


# Tests for Sunspots


def test_sunspot_number_model() -> None:
    model = SunspotNumber(
        observed_at=datetime(2026, 8, 15),
        sunspot_number=83,
    )

    assert model.sunspot_number == 83


# Tests for Aurora


def test_aurora_grid_cell_model() -> None:
    cell = AuroraGridCell(
        longitude=0,
        latitude=-90,
        aurora=3,
    )

    assert cell.longitude == 0
    assert cell.latitude == -90
    assert cell.aurora == 3


def test_aurora_forecast_model() -> None:
    model = AuroraForecast(
        observed_at=datetime(
            2026,
            8,
            15,
            22,
            10,
            tzinfo=UTC,
        ),
        forecast_at=datetime(
            2026,
            8,
            15,
            23,
            26,
            tzinfo=UTC,
        ),
        cells=[
            AuroraGridCell(
                longitude=0,
                latitude=-90,
                aurora=3,
            )
        ],
    )

    assert len(model.cells) == 1
    assert model.cells[0].aurora == 3


def test_aurora_rejects_invalid_latitude() -> None:
    with pytest.raises(ValidationError):
        AuroraGridCell(
            longitude=0,
            latitude=95,
            aurora=3,
        )


# Tests for Magnetic Field


def test_solar_magnetic_field_model() -> None:
    model = SolarMagneticField(
        observed_at=datetime(2026, 8, 15),
        total_field_nt=4.33,
        bz_gsm_nt=1.52,
        data_quality=0,
    )

    assert model.total_field_nt == 4.33
    assert model.bz_gsm_nt == 1.52


def test_solar_magnetic_field_allows_negative_bz() -> None:
    model = SolarMagneticField(
        observed_at=datetime(2026, 8, 15),
        total_field_nt=4.33,
        bz_gsm_nt=-5.2,
        data_quality=0,
    )

    assert model.bz_gsm_nt == -5.2


# Tests for Solar Wind


def test_solar_wind_model() -> None:
    model = SolarWind(
        observed_at=datetime(2026, 8, 15),
        proton_speed_kms=348.2,
        proton_density_cm3=2.75,
        proton_temperature_k=52631,
        data_quality=0,
    )

    assert model.proton_speed_kms == 348.2
    assert model.proton_density_cm3 == 2.75
    assert model.proton_temperature_k == 52631


def test_solar_wind_rejects_negative_density() -> None:
    with pytest.raises(ValidationError):
        SolarWind(
            observed_at=datetime(2026, 8, 15),
            proton_speed_kms=348.2,
            proton_density_cm3=-2.75,
            proton_temperature_k=52631,
            data_quality=0,
        )
