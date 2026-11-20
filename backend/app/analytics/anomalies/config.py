"""Versioned baseline configuration.

Every parameter that changes a baseline's numbers is part of the version
fingerprint, so editing a window, floor or threshold produces a new
``baseline_version`` instead of silently reinterpreting stored snapshots or
anomalies scored against them (Anomaly_Detection.md section 10.1).
"""

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import timedelta
from typing import Literal

Transform = Literal["log1p", "identity"]


@dataclass(frozen=True)
class MetricSpec:
    """How one rollup column becomes a baseline series."""

    name: str
    transform: Transform
    # Floor applied to MAD in model space so a flat history cannot produce
    # infinite scores. 0.5 in log1p space was carried forward from the
    # Story 5.1 synthetic evaluation (section 8.3).
    mad_floor: float
    # Count metrics: an absent rollup row in a bucket where ingestion was
    # running means zero activity. Never true for averages such as SNR.
    zero_fill: bool
    # Sparse-series guard in natural units: a cohort whose median is below
    # this is "sparse", so one-spot bursts on a quiet series are not alerts.
    min_expected_value: float = 0.0
    # Averages computed from fewer samples than this are treated as missing;
    # ``sample_count_column`` names the rollup column holding the sample count.
    min_samples_per_bucket: int = 0
    sample_count_column: str | None = None


@dataclass(frozen=True)
class CohortSpec:
    """Seasonal cohort and fallback windows for one resolution."""

    seasonal_lookback: timedelta
    seasonal_min_samples: int
    fallback_lookback: timedelta
    fallback_min_samples: int


@dataclass(frozen=True)
class BaselineConfig:
    label: str
    hourly: CohortSpec
    daily: CohortSpec
    band_metrics: tuple[MetricSpec, ...]
    station_metrics: tuple[MetricSpec, ...]
    # Station baselines are persisted only for the most active stations, so
    # storage stays bounded no matter how many callsigns are heard.
    station_limit: int
    station_selection_lookback: timedelta = field(default=timedelta(days=7))

    def cohort(self, resolution: str) -> CohortSpec:
        return self.hourly if resolution == "hour" else self.daily

    def metrics_for(self, dimension_type: str) -> tuple[MetricSpec, ...]:
        return self.band_metrics if dimension_type == "band" else self.station_metrics

    def fingerprint(self) -> str:
        payload = json.dumps(asdict(self), sort_keys=True, default=_encode)
        return hashlib.sha256(payload.encode()).hexdigest()[:10]

    @property
    def version(self) -> str:
        return f"{self.label}.{self.fingerprint()}"


def _encode(value: object) -> object:
    if isinstance(value, timedelta):
        return value.total_seconds()
    raise TypeError(f"Unsupported config value: {value!r}")


_COUNT_FLOOR = 0.5
_SNR_FLOOR_DB = 1.0
_MIN_SNR_SAMPLES = 5


def _snr_metric() -> MetricSpec:
    return MetricSpec(
        "snr_avg_db",
        "identity",
        _SNR_FLOOR_DB,
        zero_fill=False,
        min_samples_per_bucket=_MIN_SNR_SAMPLES,
        sample_count_column="snr_sample_count",
    )


DEFAULT_BASELINE_CONFIG = BaselineConfig(
    label="seasonal-mad-v1",
    hourly=CohortSpec(
        seasonal_lookback=timedelta(days=28),
        seasonal_min_samples=8,
        fallback_lookback=timedelta(days=7),
        fallback_min_samples=24,
    ),
    daily=CohortSpec(
        seasonal_lookback=timedelta(weeks=12),
        seasonal_min_samples=4,
        fallback_lookback=timedelta(days=28),
        fallback_min_samples=7,
    ),
    band_metrics=(
        MetricSpec("observation_count", "log1p", _COUNT_FLOOR, True, min_expected_value=3.0),
        MetricSpec("unique_sender_count", "log1p", _COUNT_FLOOR, True, min_expected_value=2.0),
        MetricSpec("unique_receiver_count", "log1p", _COUNT_FLOOR, True, min_expected_value=2.0),
        _snr_metric(),
    ),
    station_metrics=(
        MetricSpec("observation_count", "log1p", _COUNT_FLOOR, True, min_expected_value=3.0),
        MetricSpec(
            "unique_counterparty_count", "log1p", _COUNT_FLOOR, True, min_expected_value=2.0
        ),
        _snr_metric(),
    ),
    station_limit=500,
)
