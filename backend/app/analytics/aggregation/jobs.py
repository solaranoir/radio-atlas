from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.analytics.aggregation.queries import (
    build_daily_band_aggregation_query,
    build_daily_station_aggregation_query,
    build_hourly_band_aggregation_query,
    build_hourly_station_aggregation_query,
)


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


def run_hourly_aggregation(
    session: Session,
    *,
    bucket_start: datetime,
) -> None:
    start_time = floor_to_hour(bucket_start)
    end_time = start_time + timedelta(hours=1)

    session.execute(
        build_hourly_band_aggregation_query(
            start_time=start_time,
            end_time=end_time,
        )
    )

    for direction in ("sender", "receiver"):
        session.execute(
            build_hourly_station_aggregation_query(
                start_time=start_time,
                end_time=end_time,
                direction=direction,
            )
        )


def run_daily_aggregation(
    session: Session,
    *,
    bucket_start: datetime,
) -> None:
    start_time = floor_to_day(bucket_start)
    end_time = start_time + timedelta(days=1)

    session.execute(
        build_daily_band_aggregation_query(
            start_time=start_time,
            end_time=end_time,
        )
    )

    for direction in ("sender", "receiver"):
        session.execute(
            build_daily_station_aggregation_query(
                start_time=start_time,
                end_time=end_time,
                direction=direction,
            )
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
    current_day = floor_to_day(now)
    start_time = current_day - timedelta(days=lookback_days)

    run_daily_backfill(
        session,
        start_time=start_time,
        end_time=current_day,
    )
