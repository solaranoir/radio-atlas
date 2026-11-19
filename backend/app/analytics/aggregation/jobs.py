from datetime import UTC, datetime, timedelta

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.analytics.aggregation.persistence import (
    upsert_band_rollups,
    upsert_station_rollups,
)
from app.analytics.aggregation.queries import (
    build_daily_band_aggregation_query,
    build_daily_station_aggregation_query,
    build_hourly_band_aggregation_query,
    build_hourly_station_aggregation_query,
)
from app.infrastructure.database.models import (
    AnalyticsBandDaily,
    AnalyticsBandHourly,
    AnalyticsStationDaily,
    AnalyticsStationHourly,
    SpotRetentionDay,
)

# Namespace for per-day advisory locks shared by the daily refresh and the
# retention job ("RADA" as int4). The second key is the UTC day number.
ROLLUP_DAY_LOCK_NAMESPACE = 0x52414441
_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)


def floor_to_hour(value: datetime) -> datetime:
    return value.astimezone(UTC).replace(
        minute=0,
        second=0,
        microsecond=0,
    )


def floor_to_day(value: datetime) -> datetime:
    return value.astimezone(UTC).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )


def lock_rollup_day(session: Session, day_start: datetime) -> None:
    """Serialize work on one UTC day's rollups until the transaction ends.

    The daily refresh and the retention job both take this lock before
    deciding whether a day may be (re)aggregated from raw spots. Retention
    marks a day and only then deletes its spots, so a refresh holding the
    lock either sees the day unmarked with all its spots, or sees the marker
    and skips the day; it never aggregates a partly deleted day.
    """

    day_number = (floor_to_day(day_start) - _EPOCH).days
    session.execute(
        text("SELECT pg_advisory_xact_lock(CAST(:namespace AS integer), CAST(:day AS integer))"),
        {"namespace": ROLLUP_DAY_LOCK_NAMESPACE, "day": day_number},
    )


def is_day_retained(session: Session, day_start: datetime) -> bool:
    """True once retention has rolled up the day and may be deleting its spots."""

    return session.get(SpotRetentionDay, floor_to_day(day_start)) is not None


def run_hourly_aggregation(
    session: Session,
    *,
    bucket_start: datetime,
) -> None:
    start_time = floor_to_hour(bucket_start)
    end_time = start_time + timedelta(hours=1)

    band_result = session.execute(
        build_hourly_band_aggregation_query(
            start_time=start_time,
            end_time=end_time,
        )
    )
    upsert_band_rollups(
        session,
        model=AnalyticsBandHourly,
        rows=[dict(row) for row in band_result.mappings().all()],
    )

    for direction in ("sender", "receiver"):
        station_result = session.execute(
            build_hourly_station_aggregation_query(
                start_time=start_time,
                end_time=end_time,
                direction=direction,
            )
        )
        upsert_station_rollups(
            session,
            model=AnalyticsStationHourly,
            rows=[dict(row) for row in station_result.mappings().all()],
            direction=direction,
        )


def run_daily_aggregation(
    session: Session,
    *,
    bucket_start: datetime,
) -> None:
    start_time = floor_to_day(bucket_start)
    end_time = start_time + timedelta(days=1)

    band_result = session.execute(
        build_daily_band_aggregation_query(
            start_time=start_time,
            end_time=end_time,
        )
    )
    upsert_band_rollups(
        session,
        model=AnalyticsBandDaily,
        rows=[dict(row) for row in band_result.mappings().all()],
    )

    for direction in ("sender", "receiver"):
        station_result = session.execute(
            build_daily_station_aggregation_query(
                start_time=start_time,
                end_time=end_time,
                direction=direction,
            )
        )
        upsert_station_rollups(
            session,
            model=AnalyticsStationDaily,
            rows=[dict(row) for row in station_result.mappings().all()],
            direction=direction,
        )


def run_hourly_backfill(
    session: Session,
    *,
    start_time: datetime,
    end_time: datetime,
) -> None:
    current_bucket = floor_to_hour(start_time)
    final_bucket = floor_to_hour(end_time)

    while current_bucket < final_bucket:
        run_hourly_aggregation(
            session,
            bucket_start=current_bucket,
        )
        current_bucket += timedelta(hours=1)


def run_daily_backfill(
    session: Session,
    *,
    start_time: datetime,
    end_time: datetime,
) -> None:
    current_bucket = floor_to_day(start_time)
    final_bucket = floor_to_day(end_time)

    while current_bucket < final_bucket:
        run_daily_aggregation(
            session,
            bucket_start=current_bucket,
        )
        current_bucket += timedelta(days=1)


def run_hourly_incremental_refresh(
    session: Session,
    *,
    now: datetime,
    lookback_hours: int = 2,
) -> None:
    current_hour = floor_to_hour(now)
    start_time = current_hour - timedelta(hours=lookback_hours)

    run_hourly_backfill(
        session,
        start_time=start_time,
        end_time=current_hour,
    )


def run_daily_incremental_refresh(
    session: Session,
    *,
    now: datetime,
    lookback_days: int = 2,
) -> None:
    """Rebuild the last ``lookback_days`` completed days from raw spots.

    Days already rolled up by the retention job are skipped: their raw spots
    may be partly or fully deleted, and recomputing would overwrite the
    retention rollups with lower counts. This is what lets the raw-spot
    retention window be shorter than the refresh lookback.
    """

    current_day = floor_to_day(now)
    day = current_day - timedelta(days=lookback_days)

    while day < current_day:
        lock_rollup_day(session, day)
        if not is_day_retained(session, day):
            run_daily_aggregation(session, bucket_start=day)
        day += timedelta(days=1)
