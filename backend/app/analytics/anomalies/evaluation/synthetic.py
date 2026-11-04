"""Synthetic hourly band activity with injected, labelled anomalies.

Used to verify the harness end to end where ground truth is known. Results on
synthetic data validate the harness and illustrate detector failure modes; they
are not evidence about real PSK Reporter behavior.
"""

import math
import random
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from app.analytics.anomalies.evaluation.models import (
    EvaluationDataset,
    KnownEvent,
    SeriesKey,
    SeriesPoint,
)


@dataclass(frozen=True)
class SyntheticBand:
    key: SeriesKey
    base_rate: float
    diurnal_amplitude: float
    peak_hour_utc: int


DEFAULT_BANDS: tuple[SyntheticBand, ...] = (
    SyntheticBand(SeriesKey("20m", "FT8"), 400.0, 0.8, 16),
    SyntheticBand(SeriesKey("40m", "FT8"), 300.0, 0.9, 3),
    SyntheticBand(SeriesKey("10m", "FT8"), 80.0, 0.95, 18),
    SyntheticBand(SeriesKey("15m", "FT8"), 120.0, 0.9, 17),
    SyntheticBand(SeriesKey("80m", "FT8"), 150.0, 0.95, 5),
    SyntheticBand(SeriesKey("20m", "CW"), 25.0, 0.7, 15),
    SyntheticBand(SeriesKey("6m", "FT8"), 1.0, 0.5, 18),
    SyntheticBand(SeriesKey("160m", "FT4"), 0.6, 0.5, 6),
)


def generate_synthetic_dataset(
    *,
    days: int = 84,
    seed: int = 7,
    start: datetime = datetime(2026, 6, 1, tzinfo=UTC),
    bands: tuple[SyntheticBand, ...] = DEFAULT_BANDS,
    event_count: int = 24,
    gap_count: int = 4,
) -> EvaluationDataset:
    rng = random.Random(seed)
    hours = [start + timedelta(hours=offset) for offset in range(days * 24)]

    gaps = _choose_gaps(rng, len(hours), gap_count)
    events = _choose_events(rng, hours, bands, event_count)

    points: list[SeriesPoint] = []
    for index, hour in enumerate(hours):
        if index in gaps:
            continue
        for band in bands:
            expected = _expected_rate(band, hour)
            for event, multiplier in events:
                if event.covers(hour, band.key):
                    expected *= multiplier
            count = _poisson(rng, expected)
            if count > 0:
                points.append(SeriesPoint(bucket_start=hour, key=band.key, value=float(count)))

    return EvaluationDataset(
        points=tuple(points),
        events=tuple(event for event, _ in events),
        metric="observation_count",
        source=f"synthetic(days={days}, seed={seed})",
    )


def _expected_rate(band: SyntheticBand, hour: datetime) -> float:
    phase = 2.0 * math.pi * (hour.hour - band.peak_hour_utc) / 24.0
    diurnal = 1.0 + band.diurnal_amplitude * math.cos(phase)
    weekly = 1.25 if hour.weekday() >= 5 else 1.0
    return max(band.base_rate * diurnal * weekly, 0.0)


def _choose_events(
    rng: random.Random,
    hours: list[datetime],
    bands: tuple[SyntheticBand, ...],
    count: int,
) -> list[tuple[KnownEvent, float]]:
    # Leave the first two weeks clean so baselines can form before events.
    earliest = 14 * 24
    events: list[tuple[KnownEvent, float]] = []
    for _ in range(count):
        start = hours[rng.randrange(earliest, len(hours) - 6)]
        duration = timedelta(hours=rng.randint(2, 5))
        if rng.random() < 0.6:
            band = rng.choice(bands[:6])
            multiplier = rng.uniform(2.5, 5.0)
            label = f"opening:{band.key.label()}"
            band_name: str | None = band.key.band
        else:
            multiplier = rng.uniform(0.15, 0.4)
            label = "suppression:all-bands"
            band_name = None
        events.append(
            (KnownEvent(start=start, end=start + duration, label=label, band=band_name), multiplier)
        )
    return events


def _choose_gaps(rng: random.Random, hour_count: int, count: int) -> set[int]:
    gaps: set[int] = set()
    for _ in range(count):
        start = rng.randrange(24, hour_count - 12)
        gaps.update(range(start, start + rng.randint(2, 8)))
    return gaps


def _poisson(rng: random.Random, rate: float) -> int:
    if rate <= 0.0:
        return 0
    if rate > 50.0:
        return max(int(round(rng.gauss(rate, math.sqrt(rate)))), 0)
    threshold = math.exp(-rate)
    count, product = 0, rng.random()
    while product > threshold:
        count += 1
        product *= rng.random()
    return count
