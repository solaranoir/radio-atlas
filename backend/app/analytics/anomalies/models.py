"""Domain types for anomaly baselines (Story 5.2).

A baseline snapshot answers "what is normal for this dimension, metric and
seasonal slot, using only data before ``as_of``?". Values are held in the
metric's model space (``log1p`` for counts) because that is the space the
robust Z-score is computed in; ``expected_value`` is the center converted back
to natural units for display.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Literal

Resolution = Literal["hour", "day"]
DimensionType = Literal["band", "station"]


class BaselineMethod(StrEnum):
    # Same UTC hour (hourly) or same weekday (daily) on earlier days/weeks.
    SEASONAL_MEDIAN_MAD = "seasonal_median_mad"
    # Every recent bucket regardless of slot: a level estimate with no
    # diurnal/weekly shape, used when the seasonal cohort is too small.
    FALLBACK_RECENT_MEDIAN_MAD = "fallback_recent_median_mad"
    # Neither cohort had enough samples; no usable expectation.
    NONE = "none"


class BaselineQuality(StrEnum):
    # Seasonal cohort with enough samples, real spread and real activity.
    SUFFICIENT = "sufficient"
    # Usable only as context: fallback cohort, or so little activity that a
    # handful of spots would look extreme. Scoring should not raise alerts.
    SPARSE = "sparse"
    # Enough samples but (almost) no spread; the scale is the configured
    # floor, not an observed MAD.
    DEGENERATE = "degenerate"
    # Too few samples for any method.
    INSUFFICIENT = "insufficient"


@dataclass(frozen=True, order=True)
class DimensionKey:
    """A baseline subject: a band/mode series or a station/direction series."""

    dimension_type: DimensionType
    primary: str  # band or callsign
    secondary: str  # mode or direction

    def serialize(self) -> str:
        """Stable string key used for storage and joins."""

        if self.dimension_type == "band":
            return f"band={self.primary}|mode={self.secondary}"
        return f"callsign={self.primary}|direction={self.secondary}"

    @classmethod
    def band(cls, band: str, mode: str) -> "DimensionKey":
        return cls("band", band, mode)

    @classmethod
    def station(cls, callsign: str, direction: str) -> "DimensionKey":
        return cls("station", callsign, direction)


@dataclass(frozen=True)
class RollupValue:
    """One rollup bucket's value for one metric, already in model space.

    ``value`` is ``None`` when the bucket exists but the metric is unusable
    (for example, too few SNR samples).
    """

    bucket_start: datetime
    value: float | None


@dataclass(frozen=True)
class BaselineSnapshot:
    dimension: DimensionKey
    metric: str
    resolution: Resolution
    # UTC hour (0-23) for hourly baselines, ISO weekday (1=Mon..7=Sun) for daily.
    slot: int
    as_of: datetime
    method: BaselineMethod
    quality: BaselineQuality
    sample_count: int
    transform: str
    center: float | None
    # Robust scale actually used for scoring: max(MAD, floor). None when insufficient.
    scale: float | None
    # Raw (unfloored) MAD, kept so "degenerate" is auditable.
    mad: float | None
    expected_value: float | None
    cohort_start: datetime | None
    cohort_end: datetime | None
    baseline_version: str

    @property
    def is_usable(self) -> bool:
        return self.quality in (BaselineQuality.SUFFICIENT, BaselineQuality.DEGENERATE)
