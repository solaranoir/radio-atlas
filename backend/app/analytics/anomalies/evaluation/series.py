import math
from collections import defaultdict
from collections.abc import Iterable
from datetime import datetime

from app.analytics.anomalies.evaluation.models import Metric, SeriesKey, SeriesPoint


def prepare_series(
    points: Iterable[SeriesPoint],
    *,
    metric: Metric,
) -> dict[SeriesKey, list[SeriesPoint]]:
    """Group points into time-ordered series ready for scoring.

    Rollups only contain buckets in which a band/mode had at least one spot.
    For ``observation_count`` an absent bucket during an hour in which
    ingestion was demonstrably running (any series has data) is a true zero,
    so those hours are filled with zero. Hours with no data at all are treated
    as ingestion gaps and left absent rather than counted as silence.

    Counts are log1p-transformed so that every detector sees the same
    variance-stabilized scale; SNR averages are used as-is.
    """

    by_key: dict[SeriesKey, dict[datetime, float | None]] = defaultdict(dict)
    active_hours: set[datetime] = set()

    for point in points:
        by_key[point.key][point.bucket_start] = point.value
        active_hours.add(point.bucket_start)

    ordered_hours = sorted(active_hours)
    prepared: dict[SeriesKey, list[SeriesPoint]] = {}

    for key in sorted(by_key):
        values = by_key[key]

        if metric == "observation_count":
            prepared[key] = [
                SeriesPoint(
                    bucket_start=hour,
                    key=key,
                    value=math.log1p(max(values.get(hour) or 0.0, 0.0)),
                )
                for hour in ordered_hours
            ]
        else:
            prepared[key] = [
                SeriesPoint(bucket_start=hour, key=key, value=values[hour])
                for hour in sorted(values)
            ]

    return prepared
