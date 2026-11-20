import math
from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from app.analytics.anomalies.baseline import (
    build_metric_series,
    compute_snapshot,
    compute_snapshots,
    from_model_space,
    slot_of,
    slots_for,
    to_model_space,
)
from app.analytics.anomalies.config import DEFAULT_BASELINE_CONFIG, BaselineConfig, MetricSpec
from app.analytics.anomalies.models import (
    BaselineMethod,
    BaselineQuality,
    BaselineSnapshot,
    DimensionKey,
    Resolution,
    RollupValue,
)

CONFIG = DEFAULT_BASELINE_CONFIG
COUNT = CONFIG.band_metrics[0]  # observation_count, log1p, floor 0.5
SNR = next(spec for spec in CONFIG.band_metrics if spec.name == "snr_avg_db")
DIM = DimensionKey.band("20m", "FT8")
AS_OF = datetime(2026, 11, 20, tzinfo=UTC)  # a Friday


def _hourly(values_by_day: dict[int, float], *, hour: int) -> list[RollupValue]:
    """One value per day at ``hour``; key is days before AS_OF (1 = yesterday)."""

    return [
        RollupValue(AS_OF - timedelta(days=days_ago) + timedelta(hours=hour), value)
        for days_ago, value in sorted(values_by_day.items(), reverse=True)
    ]


def _snapshot(
    series: list[RollupValue],
    *,
    slot: int = 5,
    spec: MetricSpec = COUNT,
    resolution: Resolution = "hour",
) -> BaselineSnapshot:
    return compute_snapshot(
        dimension=DIM,
        spec=spec,
        resolution=resolution,
        slot=slot,
        as_of=AS_OF,
        series=series,
        config=CONFIG,
    )


def test_slots_follow_utc_hour_and_iso_weekday() -> None:
    assert slots_for("hour") == tuple(range(24))
    assert slots_for("day") == (1, 2, 3, 4, 5, 6, 7)
    assert slot_of(datetime(2026, 11, 20, 23, tzinfo=UTC), "hour") == 23
    assert slot_of(datetime(2026, 11, 20, tzinfo=UTC), "day") == 5  # Friday
    # A non-UTC timestamp is bucketed by its UTC hour.
    eastern = datetime(2026, 11, 20, 18, tzinfo=UTC).astimezone()
    assert slot_of(eastern, "hour") == 18


def test_model_space_round_trip() -> None:
    assert to_model_space(0.0, COUNT) == 0.0
    assert from_model_space(to_model_space(41.0, COUNT), COUNT) == pytest.approx(41.0)
    assert to_model_space(-7.5, SNR) == -7.5


def test_count_series_zero_fills_active_buckets_but_not_gaps() -> None:
    h0, h1, h2, gap = (AS_OF - timedelta(hours=n) for n in (4, 3, 2, 1))
    rows = [{"bucket_start": h0, "observation_count": 9}]

    series = build_metric_series(rows, spec=COUNT, active_buckets=[h0, h1, h2])

    assert [p.bucket_start for p in series] == [h0, h1, h2]
    assert series[0].value == pytest.approx(math.log1p(9))
    assert series[1].value == 0.0 and series[2].value == 0.0
    assert gap not in {p.bucket_start for p in series}


def test_snr_series_is_not_zero_filled_and_drops_thin_buckets() -> None:
    h0, h1, h2 = (AS_OF - timedelta(hours=n) for n in (3, 2, 1))
    rows: list[dict[str, object]] = [
        {"bucket_start": h0, "snr_avg_db": -12.0, "snr_sample_count": 40},
        {"bucket_start": h1, "snr_avg_db": 4.0, "snr_sample_count": 2},
        {"bucket_start": h2, "snr_avg_db": None, "snr_sample_count": 0},
    ]

    series = build_metric_series(rows, spec=SNR, active_buckets=[h0, h1, h2])

    assert [(p.bucket_start, p.value) for p in series] == [(h0, -12.0), (h1, None), (h2, None)]


def test_seasonal_cohort_uses_same_utc_hour_median_and_mad() -> None:
    values = {day: math.log1p(100 + 10 * (day % 3)) for day in range(1, 11)}
    other_hour = _hourly({day: 50.0 for day in range(1, 11)}, hour=6)

    snapshot = _snapshot(_hourly(values, hour=5) + other_hour)

    expected = sorted(values.values())
    center = (expected[4] + expected[5]) / 2
    assert snapshot.method is BaselineMethod.SEASONAL_MEDIAN_MAD
    assert snapshot.quality is BaselineQuality.SUFFICIENT
    assert snapshot.sample_count == 10
    assert snapshot.center == pytest.approx(center)
    assert snapshot.expected_value == pytest.approx(math.expm1(center))
    assert snapshot.mad is not None and snapshot.mad > 0
    assert snapshot.scale == max(snapshot.mad, COUNT.mad_floor)
    assert snapshot.cohort_start == AS_OF - timedelta(days=10) + timedelta(hours=5)
    assert snapshot.cohort_end == AS_OF - timedelta(days=1) + timedelta(hours=5)
    assert snapshot.baseline_version == CONFIG.version


def test_baseline_never_uses_data_at_or_after_as_of() -> None:
    history = _hourly({day: math.log1p(100) for day in range(1, 15)}, hour=5)
    future = [
        RollupValue(AS_OF + timedelta(hours=5), math.log1p(10_000)),
        RollupValue(AS_OF + timedelta(days=3, hours=5), math.log1p(10_000)),
        RollupValue(AS_OF, math.log1p(10_000)),
    ]

    assert _snapshot(history + future) == _snapshot(history)


def test_points_older_than_lookback_are_excluded() -> None:
    recent = {day: math.log1p(100) for day in range(1, 11)}
    ancient = {day: math.log1p(5_000) for day in range(29, 60)}

    snapshot = _snapshot(_hourly({**recent, **ancient}, hour=5))

    assert snapshot.sample_count == 10
    assert snapshot.expected_value == pytest.approx(100)


def test_falls_back_to_recent_level_when_seasonal_cohort_is_small() -> None:
    # Five days of hourly history: 5 same-hour samples (< 8), 120 recent buckets.
    series = [RollupValue(AS_OF - timedelta(hours=n), math.log1p(80)) for n in range(1, 5 * 24 + 1)]

    snapshot = _snapshot(series)

    assert snapshot.method is BaselineMethod.FALLBACK_RECENT_MEDIAN_MAD
    assert snapshot.quality is BaselineQuality.SPARSE
    assert snapshot.sample_count == 120
    assert snapshot.expected_value == pytest.approx(80)


def test_insufficient_history_yields_no_expectation() -> None:
    series = [RollupValue(AS_OF - timedelta(hours=n), 1.0) for n in range(1, 10)]

    snapshot = _snapshot(series)

    assert snapshot.method is BaselineMethod.NONE
    assert snapshot.quality is BaselineQuality.INSUFFICIENT
    assert snapshot.sample_count == 9
    assert snapshot.center is None and snapshot.scale is None
    assert not snapshot.is_usable


def test_flat_history_is_degenerate_with_floored_scale() -> None:
    snapshot = _snapshot(_hourly({day: math.log1p(200) for day in range(1, 12)}, hour=5))

    assert snapshot.quality is BaselineQuality.DEGENERATE
    assert snapshot.mad == 0.0
    assert snapshot.scale == COUNT.mad_floor
    assert snapshot.is_usable


def test_quiet_series_is_sparse_even_with_full_cohort() -> None:
    values = {day: math.log1p(day % 3) for day in range(1, 20)}  # medians around 1 spot

    snapshot = _snapshot(_hourly(values, hour=5))

    assert snapshot.method is BaselineMethod.SEASONAL_MEDIAN_MAD
    assert snapshot.quality is BaselineQuality.SPARSE
    assert not snapshot.is_usable


def test_missing_values_do_not_count_toward_cohort() -> None:
    values: dict[int, float] = {day: -10.0 + day % 4 for day in range(1, 8)}
    series = _hourly(values, hour=5) + [
        RollupValue(AS_OF - timedelta(days=d) + timedelta(hours=5), None) for d in range(8, 20)
    ]

    snapshot = _snapshot(series, spec=SNR)

    # 7 usable same-hour values is below the seasonal minimum of 8.
    assert snapshot.method is not BaselineMethod.SEASONAL_MEDIAN_MAD


def test_daily_cohort_uses_same_weekday() -> None:
    fridays = [RollupValue(AS_OF - timedelta(weeks=w), math.log1p(1_000)) for w in range(1, 7)]
    other_days = [
        RollupValue(AS_OF - timedelta(days=d), math.log1p(10)) for d in range(1, 42) if d % 7
    ]

    snapshot = _snapshot(fridays + other_days, slot=5, resolution="day")

    assert snapshot.method is BaselineMethod.SEASONAL_MEDIAN_MAD
    assert snapshot.sample_count == 6
    assert snapshot.expected_value == pytest.approx(1_000)


def test_compute_snapshots_returns_one_per_slot() -> None:
    hourly = compute_snapshots(
        dimension=DIM, spec=COUNT, resolution="hour", as_of=AS_OF, series=[], config=CONFIG
    )
    daily = compute_snapshots(
        dimension=DIM, spec=COUNT, resolution="day", as_of=AS_OF, series=[], config=CONFIG
    )

    assert [s.slot for s in hourly] == list(range(24))
    assert [s.slot for s in daily] == list(range(1, 8))


def test_compute_is_deterministic() -> None:
    series = _hourly({day: math.log1p(day * 7 % 13 + 20) for day in range(1, 29)}, hour=5)

    assert _snapshot(series) == _snapshot(list(reversed(series)))


def test_version_changes_with_any_parameter() -> None:
    tweaked = replace(CONFIG, hourly=replace(CONFIG.hourly, seasonal_min_samples=9))
    floor = replace(CONFIG, band_metrics=(replace(COUNT, mad_floor=0.4), *CONFIG.band_metrics[1:]))

    assert CONFIG.version == BaselineConfig(**CONFIG.__dict__).version
    assert CONFIG.version.startswith("seasonal-mad-v1.")
    assert len({CONFIG.version, tweaked.version, floor.version}) == 3


def test_dimension_keys_serialize_stably() -> None:
    assert DimensionKey.band("20m", "FT8").serialize() == "band=20m|mode=FT8"
    assert DimensionKey.station("K1ABC", "sender").serialize() == "callsign=K1ABC|direction=sender"
