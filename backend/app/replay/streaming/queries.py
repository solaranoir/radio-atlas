from datetime import datetime, timedelta

from sqlalchemy import Select, and_, func, or_, select

from app.infrastructure.database.models import AnalyticsBandHourly, Spot


def build_replay_observations_query(
    *,
    start_time: datetime,
    end_time: datetime,
    limit: int = 100,
    cursor_time: datetime | None = None,
    cursor_id: int | None = None,
) -> Select[tuple[Spot]]:
    if (cursor_time is None) != (cursor_id is None):
        raise ValueError(
            "cursor_time and cursor_id must be provided together",
        )

    query = select(Spot).where(
        Spot.observed_at >= start_time,
        Spot.observed_at < end_time,
    )

    if cursor_time is not None and cursor_id is not None:
        query = query.where(
            or_(
                Spot.observed_at > cursor_time,
                and_(
                    Spot.observed_at == cursor_time,
                    Spot.id > cursor_id,
                ),
            )
        )

    return query.order_by(
        Spot.observed_at.asc(),
        Spot.id.asc(),
    ).limit(limit)


def _floor_to_hour(value: datetime) -> datetime:
    return value.replace(
        minute=0,
        second=0,
        microsecond=0,
    )


def _ceil_to_hour(value: datetime) -> datetime:
    floor = _floor_to_hour(value)

    if value == floor:
        return floor

    return floor + timedelta(hours=1)


def build_replay_activity_query(
    *,
    start_time: datetime,
    end_time: datetime,
) -> Select[tuple[datetime, int]]:
    bucket_start_time = _floor_to_hour(start_time)
    bucket_end_time = _ceil_to_hour(end_time)

    return (
        select(
            AnalyticsBandHourly.bucket_start,
            func.sum(
                AnalyticsBandHourly.observation_count,
            ).label("observation_count"),
        )
        .where(
            AnalyticsBandHourly.bucket_start >= bucket_start_time,
            AnalyticsBandHourly.bucket_start < bucket_end_time,
        )
        .group_by(
            AnalyticsBandHourly.bucket_start,
        )
        .order_by(
            AnalyticsBandHourly.bucket_start,
        )
    )
