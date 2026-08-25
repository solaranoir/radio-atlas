from typing import Any

from app.domain import (
    Observation,
    SolarObservation,
    SpotObservation,
)
from app.providers.base import ProviderObservation


class ObservationNormalizationError(ValueError):
    """Raised when provider data cannot be normalized."""


def normalize_observation(
    observation: ProviderObservation,
) -> Observation:
    if observation.provider == "noaa":
        return normalize_noaa_observation(observation)

    if observation.provider == "psk_reporter":
        return normalize_psk_observation(observation)

    raise ObservationNormalizationError(f"Unsupported provider: {observation.provider}")


def normalize_psk_observation(
    observation: ProviderObservation,
) -> SpotObservation:
    data = observation.data

    try:
        return SpotObservation(
            provider=observation.provider,
            observed_at=data["observed_at"],
            sequence_number=data.get("sequence_number"),
            sender_callsign=data["sender_callsign"]["value"],
            receiver_callsign=data["receiver_callsign"]["value"],
            sender_grid=_nested_value(
                data.get("sender_grid"),
            ),
            receiver_grid=_nested_value(
                data.get("receiver_grid"),
            ),
            frequency_hz=_nested_value(
                data.get("frequency"),
                key="hz",
            ),
            band=_nested_value(
                data.get("band"),
            ),
            mode=data["mode"]["value"],
            snr_db=data.get("snr_db"),
            transmitted_at=data.get("transmitted_at"),
            sender_entity_id=data.get("sender_entity_id"),
            receiver_entity_id=data.get("receiver_entity_id"),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ObservationNormalizationError(
            f"PSK Reporter observation could not be normalized: {exc}"
        ) from exc


def _nested_value(
    value: object,
    *,
    key: str = "value",
) -> object | None:
    if value is None:
        return None

    if not isinstance(value, dict):
        raise ObservationNormalizationError(
            f"Expected mapping for nested value, got {type(value).__name__}"
        )

    return value.get(key)


def _get_noaa_observation_type(
    data: dict[str, Any],
) -> str:
    if "flux_sfu" in data:
        return "solar_flux"

    if "kp_index" in data:
        return "kp_index"

    if "sunspot_number" in data:
        return "sunspot_number"

    if "cells" in data:
        return "aurora"

    if "total_field_nt" in data:
        return "magnetic_field"

    if "proton_speed_kms" in data:
        return "solar_wind"

    raise ObservationNormalizationError("Unknown NOAA observation type")


def normalize_noaa_observation(
    observation: ProviderObservation,
) -> SolarObservation:
    data = observation.data

    observation_type = _get_noaa_observation_type(data)

    if observation_type == "aurora":
        return SolarObservation(
            provider=observation.provider,
            observed_at=data["observed_at"],
            observation_type="aurora",
            value=len(data["cells"]),
            unit="cells",
            data={
                "forecast_at": data.get("forecast_at"),
                "cells": data.get("cells"),
            },
        )

    if observation_type == "magnetic_field":
        return SolarObservation(
            provider=observation.provider,
            observed_at=data["observed_at"],
            observation_type="magnetic_field",
            value=data["total_field_nt"],
            unit="nT",
            data={
                "bz_gsm_nt": data.get("bz_gsm_nt"),
                "data_quality": data.get("data_quality"),
            },
        )

    if observation_type == "solar_wind":
        return SolarObservation(
            provider=observation.provider,
            observed_at=data["observed_at"],
            observation_type="solar_wind",
            value=data["proton_speed_kms"],
            unit="km/s",
            data={
                "proton_density_cm3": data.get(
                    "proton_density_cm3",
                ),
                "proton_temperature_k": data.get(
                    "proton_temperature_k",
                ),
                "data_quality": data.get(
                    "data_quality",
                ),
            },
        )

    try:
        if observation_type == "solar_flux":
            return SolarObservation(
                provider=observation.provider,
                observed_at=data["observed_at"],
                observation_type="solar_flux",
                value=data["flux_sfu"],
                unit="sfu",
                data={
                    "frequency_mhz": data.get("frequency_mhz"),
                    "reporting_schedule": data.get("reporting_schedule"),
                    "ninety_day_mean": data.get("ninety_day_mean"),
                },
            )

        if observation_type == "kp_index":
            return SolarObservation(
                provider=observation.provider,
                observed_at=data["observed_at"],
                observation_type="kp_index",
                value=data["kp_index"],
                unit="kp",
                data={
                    "estimated_kp": data.get("estimated_kp"),
                    "category": data.get("category"),
                },
            )

        if observation_type == "sunspot_number":
            return SolarObservation(
                provider=observation.provider,
                observed_at=data["observed_at"],
                observation_type="sunspot_number",
                value=data["sunspot_number"],
                unit="count",
            )

        raise ObservationNormalizationError(
            f"Unsupported NOAA observation type: {observation_type}"
        )

    except (KeyError, TypeError, ValueError) as exc:
        raise ObservationNormalizationError(
            f"NOAA observation could not be normalized: {exc}"
        ) from exc
