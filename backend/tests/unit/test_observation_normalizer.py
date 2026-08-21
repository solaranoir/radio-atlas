import pytest

from app.domain import SolarObservation, SpotObservation
from app.observations.normalizer import (
    ObservationNormalizationError,
    normalize_observation,
)
from app.providers.base import ProviderObservation


def test_normalizes_psk_observation() -> None:
    observation = ProviderObservation(
        provider="psk_reporter",
        data={
            "sequence_number": 1,
            "sender_callsign": {"value": "EA5JLN"},
            "receiver_callsign": {"value": "DL4JC"},
            "sender_grid": {"value": "IM99TN"},
            "receiver_grid": {"value": "JN39LH"},
            "frequency": {"hz": 14075361},
            "band": {"value": "20m"},
            "mode": {"value": "FT8"},
            "observed_at": "2026-08-20T20:35:44Z",
            "transmitted_at": "2026-08-20T20:35:29Z",
            "snr_db": -5,
        },
    )

    normalized = normalize_observation(observation)

    assert isinstance(normalized, SpotObservation)

    assert normalized.sender_callsign == "EA5JLN"
    assert normalized.receiver_callsign == "DL4JC"
    assert normalized.band == "20m"


def test_normalizes_kp_observation() -> None:
    observation = ProviderObservation(
        provider="noaa",
        data={
            "observed_at": "2026-08-20T00:00:00Z",
            "kp_index": 2.0,
            "estimated_kp": 1.67,
            "category": "1M",
        },
    )

    normalized = normalize_observation(observation)

    assert isinstance(normalized, SolarObservation)
    assert normalized.observation_type == "kp_index"
    assert normalized.value == 2.0
    assert normalized.unit == "kp"


def test_normalizes_solar_flux_observation() -> None:
    observation = ProviderObservation(
        provider="noaa",
        data={
            "observed_at": "2026-08-20T00:00:00Z",
            "frequency_mhz": 2800,
            "flux_sfu": 124.0,
            "reporting_schedule": "Afternoon",
            "ninety_day_mean": None,
        },
    )

    normalized = normalize_observation(observation)

    assert isinstance(normalized, SolarObservation)
    assert normalized.observation_type == "solar_flux"
    assert normalized.value == 124.0
    assert normalized.unit == "sfu"


def test_normalizes_sunspot_observation() -> None:
    observation = ProviderObservation(
        provider="noaa",
        data={
            "observed_at": "2026-08-20T00:00:00Z",
            "sunspot_number": 66,
        },
    )

    normalized = normalize_observation(observation)

    assert isinstance(normalized, SolarObservation)
    assert normalized.observation_type == "sunspot_number"
    assert normalized.value == 66
    assert normalized.unit == "count"


def test_normalizes_magnetic_field_observation() -> None:
    observation = ProviderObservation(
        provider="noaa",
        data={
            "observed_at": "2026-08-20T00:00:00Z",
            "total_field_nt": 3.56,
            "bz_gsm_nt": -0.41,
            "data_quality": 0,
        },
    )

    normalized = normalize_observation(observation)

    assert isinstance(normalized, SolarObservation)
    assert normalized.observation_type == "magnetic_field"
    assert normalized.value == 3.56
    assert normalized.unit == "nT"
    assert normalized.data["bz_gsm_nt"] == -0.41


def test_normalizes_solar_wind_observation() -> None:
    observation = ProviderObservation(
        provider="noaa",
        data={
            "observed_at": "2026-08-20T00:00:00Z",
            "proton_speed_kms": 546.1,
            "proton_density_cm3": 2.32,
            "proton_temperature_k": 164930.0,
            "data_quality": 0,
        },
    )

    normalized = normalize_observation(observation)

    assert isinstance(normalized, SolarObservation)
    assert normalized.observation_type == "solar_wind"
    assert normalized.value == 546.1
    assert normalized.unit == "km/s"


def test_normalizes_aurora_observation() -> None:
    observation = ProviderObservation(
        provider="noaa",
        data={
            "observed_at": "2026-08-20T00:00:00Z",
            "forecast_at": "2026-08-20T01:00:00Z",
            "cells": [
                {
                    "longitude": 0.0,
                    "latitude": -90.0,
                    "aurora": 5,
                },
                {
                    "longitude": 1.0,
                    "latitude": -89.0,
                    "aurora": 3,
                },
            ],
        },
    )

    normalized = normalize_observation(observation)

    assert isinstance(normalized, SolarObservation)
    assert normalized.observation_type == "aurora"
    assert normalized.value == 2
    assert normalized.unit == "cells"
    assert normalized.data["forecast_at"] == "2026-08-20T01:00:00Z"


def test_rejects_unsupported_provider() -> None:
    observation = ProviderObservation(
        provider="dx_cluster",
        data={},
    )

    with pytest.raises(
        ObservationNormalizationError,
        match="Unsupported provider",
    ):
        normalize_observation(observation)


def test_rejects_unknown_noaa_observation_type() -> None:
    observation = ProviderObservation(
        provider="noaa",
        data={
            "observed_at": "2026-08-20T00:00:00Z",
            "unexpected_field": 123,
        },
    )

    with pytest.raises(
        ObservationNormalizationError,
        match="Unknown NOAA observation type",
    ):
        normalize_observation(observation)


def test_rejects_malformed_psk_observation() -> None:
    observation = ProviderObservation(
        provider="psk_reporter",
        data={
            "sender_callsign": None,
            "receiver_callsign": {
                "value": "DL4JC",
            },
            "mode": {
                "value": "FT8",
            },
            "observed_at": "2026-08-20T20:35:44Z",
        },
    )

    with pytest.raises(
        ObservationNormalizationError,
        match="PSK Reporter observation could not be normalized",
    ):
        normalize_observation(observation)
