from dataclasses import dataclass
from datetime import datetime
from typing import Literal

Metric = Literal["observation_count", "snr_avg_db"]


@dataclass(frozen=True, order=True)
class SeriesKey:
    band: str
    mode: str

    def label(self) -> str:
        return f"{self.band}/{self.mode}"


@dataclass(frozen=True)
class SeriesPoint:
    """One hourly bucket for one band/mode series.

    ``value`` is ``None`` when the metric is unavailable for the bucket
    (for example, no SNR samples), which detectors treat as missing.
    """

    bucket_start: datetime
    key: SeriesKey
    value: float | None


@dataclass(frozen=True)
class ScoredPoint:
    """A detector's signed deviation score for one bucket.

    ``score`` is ``None`` when the detector had insufficient baseline history.
    """

    bucket_start: datetime
    key: SeriesKey
    value: float | None
    score: float | None


@dataclass(frozen=True)
class KnownEvent:
    """An independently timestamped reference event.

    ``band`` limits the event to one band; ``None`` means all bands.
    """

    start: datetime
    end: datetime
    label: str
    band: str | None = None

    def covers(self, bucket_start: datetime, key: SeriesKey) -> bool:
        if self.band is not None and self.band != key.band:
            return False
        return self.start <= bucket_start < self.end


@dataclass(frozen=True)
class EvaluationDataset:
    points: tuple[SeriesPoint, ...]
    events: tuple[KnownEvent, ...]
    metric: Metric
    source: str
