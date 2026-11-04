"""Equal-budget comparison of candidate detectors on a train/holdout split."""

import bisect
import hashlib
import math
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from app.analytics.anomalies.evaluation.detectors import Detector, median_of
from app.analytics.anomalies.evaluation.models import (
    EvaluationDataset,
    KnownEvent,
    ScoredPoint,
    SeriesKey,
    SeriesPoint,
)
from app.analytics.anomalies.evaluation.series import prepare_series

# A count series whose typical training bucket has at most this many spots is
# "sparse"; an SNR series present in less than this share of hours is sparse.
SPARSE_COUNT_MEDIAN = math.log1p(2)
SPARSE_PRESENCE_RATIO = 0.25


@dataclass(frozen=True)
class DetectorResult:
    detector: str
    threshold: float | None
    train_scored: int
    holdout_points: int
    holdout_scored: int
    train_flag_rate: float
    holdout_flag_rate: float
    holdout_flags_per_day: float
    non_event_flags_per_day: float
    diurnal_skew: float | None
    sparse_flag_share: float | None
    holdout_events: int
    event_recall: float | None
    event_score_percentile: float | None
    in_event_flag_share: float | None
    deterministic: bool

    @property
    def holdout_coverage(self) -> float:
        return _ratio(self.holdout_scored, self.holdout_points)


@dataclass(frozen=True)
class EvaluationReport:
    source: str
    metric: str
    split_at: datetime
    start: datetime
    end: datetime
    series_count: int
    sparse_series_count: int
    target_flag_rate: float
    results: tuple[DetectorResult, ...]


def evaluate(
    dataset: EvaluationDataset,
    detectors: Sequence[Detector],
    *,
    split_at: datetime,
    target_flag_rate: float,
) -> EvaluationReport:
    if not dataset.points:
        raise ValueError("Dataset contains no points to evaluate.")
    if not 0.0 < target_flag_rate < 1.0:
        raise ValueError("target_flag_rate must be between 0 and 1.")

    series = prepare_series(dataset.points, metric=dataset.metric)
    sparse_keys = _sparse_keys(series, split_at=split_at, metric=dataset.metric)
    holdout_events = tuple(event for event in dataset.events if event.start >= split_at)

    results = tuple(
        _evaluate_detector(
            detector,
            series,
            split_at=split_at,
            target_flag_rate=target_flag_rate,
            sparse_keys=sparse_keys,
            holdout_events=holdout_events,
            all_events=dataset.events,
        )
        for detector in detectors
    )

    hours = [point.bucket_start for points in series.values() for point in points]

    return EvaluationReport(
        source=dataset.source,
        metric=dataset.metric,
        split_at=split_at,
        start=min(hours),
        end=max(hours),
        series_count=len(series),
        sparse_series_count=len(sparse_keys),
        target_flag_rate=target_flag_rate,
        results=results,
    )


def default_split(points: Sequence[SeriesPoint], *, train_fraction: float = 0.7) -> datetime:
    hours = sorted({point.bucket_start for point in points})
    if len(hours) < 2:
        raise ValueError("At least two distinct buckets are required to split.")
    index = min(max(int(len(hours) * train_fraction), 1), len(hours) - 1)
    return hours[index]


def _score_all(
    detector: Detector,
    series: dict[SeriesKey, list[SeriesPoint]],
) -> list[ScoredPoint]:
    scored: list[ScoredPoint] = []
    for key in sorted(series):
        scored.extend(detector.score_series(series[key]))
    return scored


def _evaluate_detector(
    detector: Detector,
    series: dict[SeriesKey, list[SeriesPoint]],
    *,
    split_at: datetime,
    target_flag_rate: float,
    sparse_keys: set[SeriesKey],
    holdout_events: tuple[KnownEvent, ...],
    all_events: tuple[KnownEvent, ...],
) -> DetectorResult:
    scored = _score_all(detector, series)
    deterministic = _digest(scored) == _digest(_score_all(detector, series))

    train = [p for p in scored if p.bucket_start < split_at and p.score is not None]
    holdout = [p for p in scored if p.bucket_start >= split_at]
    holdout_scored = [p for p in holdout if p.score is not None]

    threshold = _calibrate(train, target_flag_rate)
    train_flags = _flags(train, threshold)
    holdout_flags = _flags(holdout_scored, threshold)

    holdout_days = len({p.bucket_start for p in holdout}) / 24.0
    non_event_flags = [
        p for p in holdout_flags if not any(e.covers(p.bucket_start, p.key) for e in all_events)
    ]
    in_event_flag_count = len(holdout_flags) - len(non_event_flags)

    return DetectorResult(
        detector=detector.name,
        threshold=threshold,
        train_scored=len(train),
        holdout_points=len(holdout),
        holdout_scored=len(holdout_scored),
        train_flag_rate=_ratio(len(train_flags), len(train)),
        holdout_flag_rate=_ratio(len(holdout_flags), len(holdout_scored)),
        holdout_flags_per_day=_ratio(len(holdout_flags), holdout_days),
        non_event_flags_per_day=_ratio(len(non_event_flags), holdout_days),
        diurnal_skew=_diurnal_skew(non_event_flags, holdout_scored),
        sparse_flag_share=(
            _ratio(sum(p.key in sparse_keys for p in holdout_flags), len(holdout_flags))
            if holdout_flags
            else None
        ),
        holdout_events=len(holdout_events),
        event_recall=_event_recall(holdout_events, holdout_flags),
        event_score_percentile=_event_score_percentile(holdout_events, holdout_scored),
        in_event_flag_share=(
            _ratio(in_event_flag_count, len(holdout_flags))
            if holdout_flags and all_events
            else None
        ),
        deterministic=deterministic,
    )


def _calibrate(train: Sequence[ScoredPoint], target_flag_rate: float) -> float | None:
    """Smallest |score| cutoff that flags at most ``target_flag_rate`` of training."""

    magnitudes = sorted(abs(p.score) for p in train if p.score is not None)
    if not magnitudes:
        return None
    allowed = int(len(magnitudes) * target_flag_rate)
    if allowed == 0:
        return math.nextafter(magnitudes[-1], math.inf)
    # Flag strictly above the (allowed + 1)-th largest magnitude.
    return math.nextafter(magnitudes[-allowed - 1], math.inf)


def _flags(points: Sequence[ScoredPoint], threshold: float | None) -> list[ScoredPoint]:
    if threshold is None:
        return []
    return [p for p in points if p.score is not None and abs(p.score) >= threshold]


def _diurnal_skew(
    flags: Sequence[ScoredPoint],
    scored: Sequence[ScoredPoint],
) -> float | None:
    """Total-variation distance between flag hours and scored-bucket hours.

    Callers pass only flags outside reference events, so genuine events that
    happen to cluster at certain hours do not register as time-of-day bias.

    0 means flags are spread across UTC hours exactly like the buckets that
    could have been flagged; values toward 1 mean flags pile up at particular
    hours, the signature of a detector mistaking the daily cycle for anomalies.
    """

    if not flags or not scored:
        return None
    flag_hours = Counter(p.bucket_start.hour for p in flags)
    base_hours = Counter(p.bucket_start.hour for p in scored)
    return 0.5 * sum(
        abs(flag_hours[h] / len(flags) - base_hours[h] / len(scored)) for h in range(24)
    )


def _event_recall(
    events: Sequence[KnownEvent],
    flags: Sequence[ScoredPoint],
) -> float | None:
    if not events:
        return None
    hit = sum(any(event.covers(p.bucket_start, p.key) for p in flags) for event in events)
    return hit / len(events)


def _event_score_percentile(
    events: Sequence[KnownEvent],
    scored: Sequence[ScoredPoint],
) -> float | None:
    """Median percentile of in-event |scores| within the holdout distribution.

    An uninformative detector sits near 0.5; a detector that ranks known
    events above ordinary comparable buckets approaches 1.0.
    """

    if not events or not scored:
        return None
    ranked = sorted(abs(p.score) for p in scored if p.score is not None)
    in_event = [
        bisect.bisect_left(ranked, abs(p.score)) / len(ranked)
        for p in scored
        if p.score is not None and any(e.covers(p.bucket_start, p.key) for e in events)
    ]
    return median_of(in_event) if in_event else None


def _sparse_keys(
    series: dict[SeriesKey, list[SeriesPoint]],
    *,
    split_at: datetime,
    metric: str,
) -> set[SeriesKey]:
    train_hours = len(
        {p.bucket_start for points in series.values() for p in points if p.bucket_start < split_at}
    )
    sparse: set[SeriesKey] = set()
    for key, points in series.items():
        train_values = [
            p.value for p in points if p.bucket_start < split_at and p.value is not None
        ]
        if not train_values:
            sparse.add(key)
        elif metric == "observation_count":
            if median_of(train_values) <= SPARSE_COUNT_MEDIAN:
                sparse.add(key)
        elif _ratio(len(train_values), train_hours) < SPARSE_PRESENCE_RATIO:
            sparse.add(key)
    return sparse


def _digest(scored: Sequence[ScoredPoint]) -> str:
    hasher = hashlib.sha256()
    for p in scored:
        score = "none" if p.score is None else f"{p.score:.9f}"
        hasher.update(f"{p.key.label()}|{p.bucket_start.isoformat()}|{score}\n".encode())
    return hasher.hexdigest()


def _ratio(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0
