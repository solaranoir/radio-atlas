import math
from datetime import UTC, datetime, timedelta

import pytest

from app.analytics.anomalies.evaluation.detectors import SeasonalMadDetector, default_detectors
from app.analytics.anomalies.evaluation.evaluation import (
    _calibrate,
    _diurnal_skew,
    default_split,
    evaluate,
)
from app.analytics.anomalies.evaluation.models import (
    EvaluationDataset,
    KnownEvent,
    ScoredPoint,
    SeriesKey,
    SeriesPoint,
)
from app.analytics.anomalies.evaluation.report import render_markdown
from app.analytics.anomalies.evaluation.series import prepare_series
from app.analytics.anomalies.evaluation.synthetic import generate_synthetic_dataset

KEY = SeriesKey("20m", "FT8")
OTHER = SeriesKey("40m", "FT8")
START = datetime(2026, 6, 1, tzinfo=UTC)


def _scored(hour: int, score: float | None) -> ScoredPoint:
    return ScoredPoint(bucket_start=START + timedelta(hours=hour), key=KEY, value=0.0, score=score)


def test_prepare_series_zero_fills_only_hours_with_ingestion() -> None:
    points = [
        SeriesPoint(bucket_start=START, key=KEY, value=9.0),
        SeriesPoint(bucket_start=START + timedelta(hours=1), key=OTHER, value=4.0),
        # Hour 2 has no data anywhere: an ingestion gap, not silence.
        SeriesPoint(bucket_start=START + timedelta(hours=3), key=KEY, value=0.0),
    ]

    series = prepare_series(points, metric="observation_count")

    assert [p.bucket_start.hour for p in series[KEY]] == [0, 1, 3]
    assert [p.value for p in series[KEY]] == pytest.approx([math.log1p(9.0), 0.0, 0.0])
    assert [p.value for p in series[OTHER]] == pytest.approx([0.0, math.log1p(4.0), 0.0])


def test_prepare_series_keeps_snr_sparse_and_untransformed() -> None:
    points = [
        SeriesPoint(bucket_start=START, key=KEY, value=-12.5),
        SeriesPoint(bucket_start=START + timedelta(hours=1), key=OTHER, value=-3.0),
    ]

    series = prepare_series(points, metric="snr_avg_db")

    assert [p.value for p in series[KEY]] == [-12.5]


def test_calibrate_flags_at_most_the_target_share() -> None:
    train = [_scored(h, float(h)) for h in range(100)]

    threshold = _calibrate(train, 0.05)

    assert threshold is not None
    assert sum(abs(p.score or 0.0) >= threshold for p in train) == 5


def test_calibrate_with_tiny_budget_flags_nothing_and_handles_empty() -> None:
    train = [_scored(h, float(h)) for h in range(10)]
    threshold = _calibrate(train, 0.01)

    assert threshold is not None
    assert all(abs(p.score or 0.0) < threshold for p in train)
    assert _calibrate([], 0.01) is None


def test_diurnal_skew_is_zero_when_flags_match_base_hours() -> None:
    scored = [_scored(h, 1.0) for h in range(48)]

    assert _diurnal_skew(scored, scored) == pytest.approx(0.0)
    assert _diurnal_skew([scored[3], scored[27]], scored) == pytest.approx(23 / 24)
    assert _diurnal_skew([], scored) is None


def test_known_event_band_scope() -> None:
    event = KnownEvent(start=START, end=START + timedelta(hours=2), label="x", band="20m")

    assert event.covers(START + timedelta(hours=1), KEY)
    assert not event.covers(START + timedelta(hours=1), OTHER)
    assert not event.covers(START + timedelta(hours=2), KEY)


def test_default_split_uses_train_fraction() -> None:
    points = [
        SeriesPoint(bucket_start=START + timedelta(hours=h), key=KEY, value=1.0) for h in range(10)
    ]

    assert default_split(points, train_fraction=0.7) == START + timedelta(hours=7)
    with pytest.raises(ValueError):
        default_split(points[:1])


def test_evaluate_rejects_bad_inputs() -> None:
    empty = EvaluationDataset(points=(), events=(), metric="observation_count", source="t")
    with pytest.raises(ValueError):
        evaluate(empty, default_detectors(), split_at=START, target_flag_rate=0.01)

    dataset = generate_synthetic_dataset(days=20, event_count=2, gap_count=0)
    with pytest.raises(ValueError):
        evaluate(dataset, default_detectors(), split_at=START, target_flag_rate=1.5)


def test_synthetic_evaluation_is_reproducible_and_rewards_seasonal_baseline() -> None:
    dataset = generate_synthetic_dataset(days=56, seed=3, event_count=16)
    assert dataset == generate_synthetic_dataset(days=56, seed=3, event_count=16)

    split_at = default_split(dataset.points)
    report = evaluate(dataset, default_detectors(), split_at=split_at, target_flag_rate=0.005)
    results = {r.detector: r for r in report.results}

    assert report.series_count == 8
    assert all(r.deterministic for r in report.results)
    assert all(abs(r.train_flag_rate - 0.005) < 0.001 for r in report.results)

    seasonal = results["seasonal-mad-floor0.5"]
    rolling = results["rolling-mean-24h"]
    assert seasonal.event_score_percentile is not None
    assert rolling.event_score_percentile is not None
    assert seasonal.event_score_percentile > rolling.event_score_percentile
    assert seasonal.holdout_coverage > 0.9


def test_evaluate_reports_no_event_metrics_without_events() -> None:
    synthetic = generate_synthetic_dataset(days=21, event_count=0, gap_count=0)
    dataset = EvaluationDataset(
        points=synthetic.points, events=(), metric="observation_count", source="t"
    )

    report = evaluate(
        dataset,
        [SeasonalMadDetector()],
        split_at=default_split(dataset.points),
        target_flag_rate=0.01,
    )

    result = report.results[0]
    assert result.holdout_events == 0
    assert result.event_recall is None
    assert result.event_score_percentile is None
    assert result.in_event_flag_share is None


def test_render_markdown_lists_every_detector() -> None:
    dataset = generate_synthetic_dataset(days=21, event_count=4, gap_count=1)
    report = evaluate(
        dataset,
        default_detectors(),
        split_at=default_split(dataset.points),
        target_flag_rate=0.01,
    )

    markdown = render_markdown(report)

    for detector in default_detectors():
        assert f"`{detector.name}`" in markdown
    assert "Alert budget" in markdown
