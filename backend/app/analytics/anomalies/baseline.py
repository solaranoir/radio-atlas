"""Seasonal robust baselines: pure, deterministic and strictly causal.

Nothing here touches the database. Given a dimension's rollup history, a
metric, a resolution and a cut-off ``as_of``, it returns one snapshot per
seasonal slot. Only buckets that start strictly before ``as_of`` are used,
whatever the caller passes in, so a baseline can never see the bucket it will
later be compared with.

Cohorts (Anomaly_Detection.md section 6.2):

* hourly: the same UTC hour on earlier days within ``seasonal_lookback``;
  if too few, every hourly bucket within ``fallback_lookback``.
* daily: the same ISO weekday on earlier weeks; if too few, every daily
  bucket within ``fallback_lookback``.
"""

import math
from collections.abc import Iterable, Mapping, Sequence
from datetime import UTC, datetime
from typing import Any

from app.analytics.anomalies.config import BaselineConfig, MetricSpec
from app.analytics.anomalies.models import (
    BaselineMethod,
    BaselineQuality,
    BaselineSnapshot,
    DimensionKey,
    Resolution,
    RollupValue,
)
from app.analytics.anomalies.robust import median_absolute_deviation, median_of

# MAD at or below this is treated as "no observed spread".
_ZERO_SPREAD = 1e-9

HOURLY_SLOTS = tuple(range(24))
DAILY_SLOTS = tuple(range(1, 8))


def slots_for(resolution: Resolution) -> tuple[int, ...]:
    return HOURLY_SLOTS if resolution == "hour" else DAILY_SLOTS


def slot_of(bucket_start: datetime, resolution: Resolution) -> int:
    """UTC hour for hourly buckets, ISO weekday (1=Monday) for daily buckets."""

    utc = bucket_start.astimezone(UTC)
    return utc.hour if resolution == "hour" else utc.isoweekday()


def to_model_space(value: float, spec: MetricSpec) -> float:
    return math.log1p(max(value, 0.0)) if spec.transform == "log1p" else value


def from_model_space(value: float, spec: MetricSpec) -> float:
    return math.expm1(value) if spec.transform == "log1p" else value


def build_metric_series(
    rows: Iterable[Mapping[str, Any]],
    *,
    spec: MetricSpec,
    active_buckets: Iterable[datetime],
) -> list[RollupValue]:
    """Turn one dimension's rollup rows into a time-ordered model-space series.

    ``rows`` carry ``bucket_start`` plus rollup columns. Count metrics are
    zero-filled over ``active_buckets`` (buckets in which ingestion was
    demonstrably running); other buckets with no row are ingestion gaps and
    stay absent, so an outage never looks like a quiet band.
    """

    by_bucket: dict[datetime, float | None] = {}
    for row in rows:
        raw = row[spec.name]
        usable = raw is not None
        if usable and spec.sample_count_column is not None:
            usable = (row[spec.sample_count_column] or 0) >= spec.min_samples_per_bucket
        by_bucket[row["bucket_start"]] = (
            to_model_space(float(raw), spec) if usable and raw is not None else None
        )

    if spec.zero_fill:
        zero = to_model_space(0.0, spec)
        for bucket in active_buckets:
            by_bucket.setdefault(bucket, zero)

    return [RollupValue(bucket, by_bucket[bucket]) for bucket in sorted(by_bucket)]


def compute_snapshot(
    *,
    dimension: DimensionKey,
    spec: MetricSpec,
    resolution: Resolution,
    slot: int,
    as_of: datetime,
    series: Sequence[RollupValue],
    config: BaselineConfig,
) -> BaselineSnapshot:
    cohort_spec = config.cohort(resolution)
    history = [p for p in series if p.bucket_start < as_of and p.value is not None]

    seasonal_start = as_of - cohort_spec.seasonal_lookback
    cohort = [
        p
        for p in history
        if p.bucket_start >= seasonal_start and slot_of(p.bucket_start, resolution) == slot
    ]
    method = BaselineMethod.SEASONAL_MEDIAN_MAD

    if len(cohort) < cohort_spec.seasonal_min_samples:
        fallback_start = as_of - cohort_spec.fallback_lookback
        cohort = [p for p in history if p.bucket_start >= fallback_start]
        method = BaselineMethod.FALLBACK_RECENT_MEDIAN_MAD
        if len(cohort) < cohort_spec.fallback_min_samples:
            return _insufficient(
                dimension, spec, resolution, slot, as_of, len(cohort), config.version
            )

    values = [p.value for p in cohort if p.value is not None]
    center = median_of(values)
    mad = median_absolute_deviation(values, center=center)
    expected = from_model_space(center, spec)

    return BaselineSnapshot(
        dimension=dimension,
        metric=spec.name,
        resolution=resolution,
        slot=slot,
        as_of=as_of,
        method=method,
        quality=_quality(method, expected=expected, mad=mad, spec=spec),
        sample_count=len(values),
        transform=spec.transform,
        center=center,
        scale=max(mad, spec.mad_floor),
        mad=mad,
        expected_value=expected,
        cohort_start=min(p.bucket_start for p in cohort),
        cohort_end=max(p.bucket_start for p in cohort),
        baseline_version=config.version,
    )


def compute_snapshots(
    *,
    dimension: DimensionKey,
    spec: MetricSpec,
    resolution: Resolution,
    as_of: datetime,
    series: Sequence[RollupValue],
    config: BaselineConfig,
) -> list[BaselineSnapshot]:
    """One snapshot per seasonal slot for a dimension/metric/resolution."""

    return [
        compute_snapshot(
            dimension=dimension,
            spec=spec,
            resolution=resolution,
            slot=slot,
            as_of=as_of,
            series=series,
            config=config,
        )
        for slot in slots_for(resolution)
    ]


def _quality(
    method: BaselineMethod,
    *,
    expected: float,
    mad: float,
    spec: MetricSpec,
) -> BaselineQuality:
    if method is not BaselineMethod.SEASONAL_MEDIAN_MAD:
        return BaselineQuality.SPARSE
    if spec.min_expected_value and expected < spec.min_expected_value:
        return BaselineQuality.SPARSE
    if mad <= _ZERO_SPREAD:
        return BaselineQuality.DEGENERATE
    return BaselineQuality.SUFFICIENT


def _insufficient(
    dimension: DimensionKey,
    spec: MetricSpec,
    resolution: Resolution,
    slot: int,
    as_of: datetime,
    sample_count: int,
    version: str,
) -> BaselineSnapshot:
    return BaselineSnapshot(
        dimension=dimension,
        metric=spec.name,
        resolution=resolution,
        slot=slot,
        as_of=as_of,
        method=BaselineMethod.NONE,
        quality=BaselineQuality.INSUFFICIENT,
        sample_count=sample_count,
        transform=spec.transform,
        center=None,
        scale=None,
        mad=None,
        expected_value=None,
        cohort_start=None,
        cohort_end=None,
        baseline_version=version,
    )
