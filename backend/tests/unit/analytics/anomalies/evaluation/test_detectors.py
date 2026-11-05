import math
from datetime import UTC, datetime, timedelta

import pytest

from app.analytics.anomalies.evaluation.detectors import (
    Detector,
    RollingMeanDetector,
    SeasonalMadDetector,
    ThresholdDetector,
    ZScoreDetector,
    default_detectors,
    median_of,
)
from app.analytics.anomalies.evaluation.models import SeriesKey, SeriesPoint

KEY = SeriesKey("20m", "FT8")
START = datetime(2026, 6, 1, tzinfo=UTC)


def _diurnal_series(days: int, *, spike_at: int | None = None) -> list[SeriesPoint]:
    points = []
    for offset in range(days * 24):
        hour = START + timedelta(hours=offset)
        value = 5.0 + 2.0 * math.cos(2.0 * math.pi * hour.hour / 24.0)
        if offset == spike_at:
            value += 3.0
        points.append(SeriesPoint(bucket_start=hour, key=KEY, value=value))
    return points


@pytest.mark.parametrize("detector", default_detectors(), ids=lambda d: d.name)
def test_detectors_are_causal(detector: Detector) -> None:
    series = _diurnal_series(20)
    altered = series[:300] + [
        SeriesPoint(bucket_start=p.bucket_start, key=KEY, value=(p.value or 0.0) * 10.0)
        for p in series[300:]
    ]

    original_scores = [p.score for p in detector.score_series(series)[:301]]
    altered_scores = [p.score for p in detector.score_series(altered)[:301]]

    # The bucket at index 300 itself changed, so compare strictly earlier buckets.
    assert original_scores[:300] == altered_scores[:300]


@pytest.mark.parametrize("detector", default_detectors(), ids=lambda d: d.name)
def test_detectors_return_one_score_per_point_and_skip_missing(detector: Detector) -> None:
    series = _diurnal_series(12)
    series[200] = SeriesPoint(bucket_start=series[200].bucket_start, key=KEY, value=None)

    scored = detector.score_series(series)

    assert [p.bucket_start for p in scored] == [p.bucket_start for p in series]
    assert scored[200].score is None
    assert scored[0].score is None


def test_seasonal_mad_ignores_regular_daily_cycle_that_rolling_mean_flags() -> None:
    series = _diurnal_series(20)

    seasonal = SeasonalMadDetector().score_series(series)
    rolling = RollingMeanDetector().score_series(series)

    tail = slice(-48, None)
    assert max(abs(p.score or 0.0) for p in seasonal[tail]) < 1e-9
    assert max(abs(p.score or 0.0) for p in rolling[tail]) > 1.0


def test_seasonal_mad_scores_spike_against_same_hour_cohort() -> None:
    spike_index = 18 * 24 + 7
    scored = SeasonalMadDetector(mad_floor=0.5).score_series(
        _diurnal_series(20, spike_at=spike_index)
    )

    expected = 0.6745 * 3.0 / 0.5
    assert scored[spike_index].score == pytest.approx(expected)


def test_seasonal_mad_reports_insufficient_baseline_until_cohort_is_full() -> None:
    detector = SeasonalMadDetector(minimum_samples=8)
    scored = detector.score_series(_diurnal_series(10))

    noon = [p for p in scored if p.bucket_start.hour == 12]
    assert [p.score is None for p in noon] == [True] * 8 + [False] * 2


def test_seasonal_mad_floor_bounds_scores_on_flat_history() -> None:
    flat = [
        SeriesPoint(bucket_start=START + timedelta(days=day), key=KEY, value=0.0)
        for day in range(10)
    ]
    flat.append(SeriesPoint(bucket_start=START + timedelta(days=10), key=KEY, value=1.0))

    scored = SeasonalMadDetector(mad_floor=0.5).score_series(flat)

    assert scored[-1].score == pytest.approx(0.6745 * 1.0 / 0.5)


def test_seasonal_mad_lookback_evicts_old_cohort_values() -> None:
    detector = SeasonalMadDetector(lookback=timedelta(days=3), minimum_samples=3)
    series = [
        SeriesPoint(bucket_start=START + timedelta(days=day), key=KEY, value=float(day))
        for day in range(6)
    ]

    scored = detector.score_series(series)

    # Day 5 sees only days 2, 3, 4 (median 3, MAD 1).
    assert scored[5].score == pytest.approx(0.6745 * 2.0)


def test_threshold_detector_scores_against_running_median() -> None:
    series = [
        SeriesPoint(bucket_start=START + timedelta(hours=h), key=KEY, value=float(h % 3))
        for h in range(30)
    ]

    scored = ThresholdDetector(minimum_samples=24).score_series(series)

    assert all(p.score is None for p in scored[:24])
    assert scored[24].score == pytest.approx(0.0 - 1.0)


def test_zscore_uses_floor_for_constant_window() -> None:
    series = [
        SeriesPoint(bucket_start=START + timedelta(hours=h), key=KEY, value=2.0) for h in range(60)
    ]
    series.append(SeriesPoint(bucket_start=START + timedelta(hours=60), key=KEY, value=3.0))

    scored = ZScoreDetector(minimum_samples=48, std_floor=0.25).score_series(series)

    assert scored[-1].score == pytest.approx(4.0)


def test_default_detector_names_are_unique() -> None:
    names = [detector.name for detector in default_detectors()]
    assert len(names) == len(set(names))


def test_median_of_handles_odd_and_even_lengths() -> None:
    assert median_of([3.0, 1.0, 2.0]) == 2.0
    assert median_of([4.0, 1.0, 3.0, 2.0]) == 2.5
