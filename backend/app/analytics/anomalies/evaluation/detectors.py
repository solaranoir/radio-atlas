"""Candidate detectors compared by the Story 5.1 evaluation.

Every detector is strictly causal: the score for a bucket depends only on
buckets strictly earlier in the same series. Each returns a signed score where
larger magnitude means "more unusual"; flagging thresholds are calibrated
separately so detectors are compared at an equal alert budget.
"""

import bisect
import math
from collections import deque
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol

from app.analytics.anomalies.evaluation.models import ScoredPoint, SeriesPoint

# Scales MAD to be a consistent estimator of the standard deviation for
# normally distributed data (Iglewicz & Hoaglin modified Z-score).
MAD_CONSISTENCY = 0.6745


class Detector(Protocol):
    @property
    def name(self) -> str: ...

    def score_series(self, series: Sequence[SeriesPoint]) -> list[ScoredPoint]: ...


def _scored(point: SeriesPoint, score: float | None) -> ScoredPoint:
    return ScoredPoint(
        bucket_start=point.bucket_start,
        key=point.key,
        value=point.value,
        score=score,
    )


class _TimeWindow:
    """Values observed within a trailing time window, with running moments."""

    def __init__(self, span: timedelta) -> None:
        self._span = span
        self._items: deque[tuple[datetime, float]] = deque()
        self._sum = 0.0
        self._sum_sq = 0.0

    def evict_before(self, now: datetime) -> None:
        cutoff = now - self._span
        while self._items and self._items[0][0] < cutoff:
            _, value = self._items.popleft()
            self._sum -= value
            self._sum_sq -= value * value

    def add(self, at: datetime, value: float) -> None:
        self._items.append((at, value))
        self._sum += value
        self._sum_sq += value * value

    def __len__(self) -> int:
        return len(self._items)

    def mean_std(self) -> tuple[float, float]:
        count = len(self._items)
        mean = self._sum / count
        variance = max(self._sum_sq / count - mean * mean, 0.0)
        return mean, math.sqrt(variance)

    def values(self) -> list[float]:
        return [value for _, value in self._items]


@dataclass(frozen=True)
class ThresholdDetector:
    """Static level threshold: deviation from the series' long-run median.

    Represents the "threshold-only" baseline: no recency and no seasonality,
    only a fixed per-series reference level learned from all prior history.
    """

    minimum_samples: int = 24
    name: str = "threshold-static"

    def score_series(self, series: Sequence[SeriesPoint]) -> list[ScoredPoint]:
        history: list[float] = []
        scored: list[ScoredPoint] = []

        for point in series:
            score: float | None = None
            if point.value is not None and len(history) >= self.minimum_samples:
                score = point.value - _sorted_median(history)
            scored.append(_scored(point, score))
            if point.value is not None:
                bisect.insort(history, point.value)

        return scored


@dataclass(frozen=True)
class RollingMeanDetector:
    """Deviation from the mean of the immediately preceding window."""

    window: timedelta = timedelta(hours=24)
    minimum_samples: int = 12
    std_floor: float = 0.1
    name: str = "rolling-mean-24h"

    def score_series(self, series: Sequence[SeriesPoint]) -> list[ScoredPoint]:
        return _windowed_zscore(series, self.window, self.minimum_samples, self.std_floor)


@dataclass(frozen=True)
class ZScoreDetector:
    """Classic mean/standard-deviation Z-score over a long trailing window."""

    window: timedelta = timedelta(days=28)
    minimum_samples: int = 48
    std_floor: float = 0.1
    name: str = "zscore-28d"

    def score_series(self, series: Sequence[SeriesPoint]) -> list[ScoredPoint]:
        return _windowed_zscore(series, self.window, self.minimum_samples, self.std_floor)


@dataclass(frozen=True)
class SeasonalMadDetector:
    """Selected candidate: robust modified Z-score within an hour-of-day cohort.

    The baseline for a bucket is the median of the same UTC hour on prior days
    within ``lookback``; spread is the MAD of that cohort, floored so that a
    perfectly flat history cannot produce infinite scores. Cohorts with fewer
    than ``minimum_samples`` values yield "insufficient baseline" (``None``).
    """

    lookback: timedelta = timedelta(days=28)
    minimum_samples: int = 8
    mad_floor: float = 0.1
    name: str = "seasonal-mad"

    def score_series(self, series: Sequence[SeriesPoint]) -> list[ScoredPoint]:
        cohorts: dict[int, _TimeWindow] = {}
        scored: list[ScoredPoint] = []

        for point in series:
            cohort = cohorts.setdefault(point.bucket_start.hour, _TimeWindow(self.lookback))
            cohort.evict_before(point.bucket_start)

            score: float | None = None
            if point.value is not None and len(cohort) >= self.minimum_samples:
                values = cohort.values()
                median = median_of(values)
                mad = median_of([abs(value - median) for value in values])
                score = MAD_CONSISTENCY * (point.value - median) / max(mad, self.mad_floor)

            scored.append(_scored(point, score))
            if point.value is not None:
                cohort.add(point.bucket_start, point.value)

        return scored


def default_detectors() -> list[Detector]:
    return [
        ThresholdDetector(),
        RollingMeanDetector(),
        ZScoreDetector(),
        SeasonalMadDetector(mad_floor=0.1, name="seasonal-mad-floor0.1"),
        SeasonalMadDetector(mad_floor=0.5, name="seasonal-mad-floor0.5"),
    ]


def _windowed_zscore(
    series: Sequence[SeriesPoint],
    span: timedelta,
    minimum_samples: int,
    std_floor: float,
) -> list[ScoredPoint]:
    window = _TimeWindow(span)
    scored: list[ScoredPoint] = []

    for point in series:
        window.evict_before(point.bucket_start)

        score: float | None = None
        if point.value is not None and len(window) >= minimum_samples:
            mean, std = window.mean_std()
            score = (point.value - mean) / max(std, std_floor)

        scored.append(_scored(point, score))
        if point.value is not None:
            window.add(point.bucket_start, point.value)

    return scored


def median_of(values: Sequence[float]) -> float:
    """Median of a non-empty sequence (sorts a copy)."""

    return _sorted_median(sorted(values))


def _sorted_median(values: Sequence[float]) -> float:
    middle = len(values) // 2
    if len(values) % 2:
        return values[middle]
    return (values[middle - 1] + values[middle]) / 2.0
