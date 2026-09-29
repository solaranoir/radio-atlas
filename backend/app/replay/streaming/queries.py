from datetime import datetime

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

def build_replay_activity_query(
    *,
    start_time: datetime,
    end_time: datetime,
) -> Select[tuple[datetime, int]]:
    return (
        select(
            AnalyticsBandHourly.bucket_start,
            func.sum(
                AnalyticsBandHourly.observation_count,
            ).label("observation_count"),
        )
        .where(
            AnalyticsBandHourly.bucket_start >= start_time,
            AnalyticsBandHourly.bucket_start < end_time,
        )
        .group_by(
            AnalyticsBandHourly.bucket_start,
        )
        .order_by(
            AnalyticsBandHourly.bucket_start,
        )
    )
