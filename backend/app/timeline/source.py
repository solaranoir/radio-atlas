from datetime import datetime, timedelta

from sqlalchemy import DateTime, Integer, and_, column, func, select, values
from sqlalchemy.orm import Session

from app.infrastructure.database.models import AnalyticsBandDaily, AnalyticsBandHourly, Spot
from app.timeline.models import Resolution


def boundary_intervals(
    start: datetime, end: datetime, resolution: Resolution
) -> list[tuple[datetime, datetime]]:
    if resolution == "minute":
        return [(start, end)]
    floor_start = start.replace(minute=0, second=0, microsecond=0)
    floor_end = end.replace(minute=0, second=0, microsecond=0)
    if resolution == "day":
        floor_start = floor_start.replace(hour=0)
        floor_end = floor_end.replace(hour=0)
    unit = timedelta(hours=1) if resolution == "hour" else timedelta(days=1)
    first_end = start
    edges = []
    if start != floor_start:
        try:
            first_end = min(floor_start + unit, end)
        except OverflowError:
            first_end = end
        edges.append((start, first_end))
    last_start = max(start, first_end, floor_end)
    if last_start < end:
        edges.append((last_start, end))
    return edges


class TimelineSource:
    def __init__(self, session: Session) -> None:
        self.session = session

    def history_bounds(self) -> tuple[datetime | None, datetime | None]:
        row = self.session.execute(
            select(func.min(Spot.observed_at), func.max(Spot.observed_at))
        ).one()
        return row[0], row[1]

    def counts(
        self, intervals: list[tuple[datetime, datetime]], resolution: Resolution
    ) -> list[int]:
        # Join bounded display intervals once per source, rather than one query per bucket.
        ranges = (
            values(
                column("index", Integer),
                column("start_time", DateTime(timezone=True)),
                column("end_time", DateTime(timezone=True)),
            )
            .data([(index, start, end) for index, (start, end) in enumerate(intervals)])
            .cte("ranges")
        )
        counts = [0] * len(intervals)
        if resolution != "minute":
            unit = timedelta(hours=1) if resolution == "hour" else timedelta(days=1)
            model = AnalyticsBandHourly if resolution == "hour" else AnalyticsBandDaily
            full = and_(
                model.bucket_start >= ranges.c.start_time,
                model.bucket_start + unit <= ranges.c.end_time,
            )
            rollups = (
                select(ranges.c.index, func.sum(model.observation_count))
                .select_from(ranges.join(model, full))
                .group_by(ranges.c.index)
            )
            for index, count in self.session.execute(rollups):
                counts[index] = int(count)
        edges = [
            (index, start, end)
            for index, (lower, upper) in enumerate(intervals)
            for start, end in boundary_intervals(lower, upper, resolution)
        ]
        if not edges:
            return counts
        raw_ranges = (
            values(
                column("index", Integer),
                column("start_time", DateTime(timezone=True)),
                column("end_time", DateTime(timezone=True)),
            )
            .data(edges)
            .cte("raw_ranges")
        )
        raw = select(raw_ranges.c.index, func.count(Spot.id)).select_from(
            raw_ranges.join(
                Spot,
                and_(
                    Spot.observed_at >= raw_ranges.c.start_time,
                    Spot.observed_at < raw_ranges.c.end_time,
                ),
            )
        )
        if resolution != "minute":
            raw = raw.where(Spot.band.is_not(None))
        for index, count in self.session.execute(raw.group_by(raw_ranges.c.index)):
            counts[index] += int(count)
        return counts
