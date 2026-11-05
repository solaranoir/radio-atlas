"""Load evaluation datasets from the rollup database or CSV exports.

Reads are read-only. Point the database loader at a replica or a restored
snapshot rather than the live production primary where possible.
"""

import csv
from collections.abc import Iterable
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.anomalies.evaluation.models import (
    EvaluationDataset,
    KnownEvent,
    Metric,
    SeriesKey,
    SeriesPoint,
)
from app.infrastructure.database.models import AnalyticsBandHourly, SolarCondition

KP_STORM_THRESHOLD = 5.0
KP_WINDOW = timedelta(hours=3)


def load_from_database(
    session: Session,
    *,
    metric: Metric,
    start: datetime | None = None,
    end: datetime | None = None,
    kp_threshold: float = KP_STORM_THRESHOLD,
) -> EvaluationDataset:
    rollups = select(
        AnalyticsBandHourly.bucket_start,
        AnalyticsBandHourly.band,
        AnalyticsBandHourly.mode,
        AnalyticsBandHourly.observation_count,
        AnalyticsBandHourly.snr_avg_db,
    ).order_by(AnalyticsBandHourly.bucket_start)
    kp = (
        select(SolarCondition.observed_at)
        .where(
            SolarCondition.observation_type == "kp_index",
            SolarCondition.value >= kp_threshold,
        )
        .order_by(SolarCondition.observed_at)
    )
    if start is not None:
        rollups = rollups.where(AnalyticsBandHourly.bucket_start >= start)
        kp = kp.where(SolarCondition.observed_at >= start)
    if end is not None:
        rollups = rollups.where(AnalyticsBandHourly.bucket_start < end)
        kp = kp.where(SolarCondition.observed_at < end)

    points = tuple(
        _point(row.bucket_start, row.band, row.mode, row.observation_count, row.snr_avg_db, metric)
        for row in session.execute(rollups)
    )
    storm_times = [row.observed_at for row in session.execute(kp)]

    return EvaluationDataset(
        points=points,
        events=tuple(kp_storm_events(storm_times, threshold=kp_threshold)),
        metric=metric,
        source="database:analytics_band_hourly",
    )


def load_points_csv(path: Path, *, metric: Metric) -> tuple[SeriesPoint, ...]:
    """Columns: bucket_start, band, mode, observation_count, snr_avg_db."""

    with path.open(newline="") as handle:
        return tuple(
            _point(
                _parse_time(row["bucket_start"]),
                row["band"],
                row["mode"],
                int(row["observation_count"]),
                float(row["snr_avg_db"]) if row.get("snr_avg_db") else None,
                metric,
            )
            for row in csv.DictReader(handle)
        )


def load_events_csv(path: Path) -> tuple[KnownEvent, ...]:
    """Columns: start, end, label, and optional band."""

    with path.open(newline="") as handle:
        return tuple(
            KnownEvent(
                start=_parse_time(row["start"]),
                end=_parse_time(row["end"]),
                label=row["label"],
                band=row.get("band") or None,
            )
            for row in csv.DictReader(handle)
        )


def kp_storm_events(
    observed_at: Iterable[datetime],
    *,
    threshold: float = KP_STORM_THRESHOLD,
) -> list[KnownEvent]:
    """Merge storm-level Kp readings into contiguous all-band event windows.

    Each reading covers the following three-hour Kp interval; overlapping or
    touching intervals collapse into a single event.
    """

    windows: list[list[datetime]] = []
    for at in sorted(observed_at):
        end = at + KP_WINDOW
        if windows and at <= windows[-1][1]:
            windows[-1][1] = max(windows[-1][1], end)
        else:
            windows.append([at, end])
    return [KnownEvent(start=start, end=end, label=f"kp>={threshold:g}") for start, end in windows]


def _point(
    bucket_start: datetime,
    band: str,
    mode: str,
    observation_count: int,
    snr_avg_db: float | None,
    metric: Metric,
) -> SeriesPoint:
    value: float | None
    if metric == "observation_count":
        value = float(observation_count)
    else:
        value = None if snr_avg_db is None else float(snr_avg_db)
    return SeriesPoint(bucket_start=bucket_start, key=SeriesKey(band, mode), value=value)


def _parse_time(text: str) -> datetime:
    parsed = datetime.fromisoformat(text.strip().replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"Timestamp must include a UTC offset: {text!r}")
    return parsed
