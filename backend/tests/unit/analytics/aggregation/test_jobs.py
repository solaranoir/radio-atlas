from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session

from app.analytics.aggregation.jobs import (
    floor_to_day,
    floor_to_hour,
    run_daily_aggregation,
    run_daily_backfill,
    run_daily_incremental_refresh,
    run_hourly_aggregation,
    run_hourly_backfill,
    run_hourly_incremental_refresh,
)


def test_hourly_aggregation_executes_three_queries() -> None:
    session = MagicMock(spec=Session)

    run_hourly_aggregation(
        session,
        bucket_start=datetime(
            2026,
            9,
            19,
            14,
            37,
            tzinfo=UTC,
        ),
    )

    assert session.execute.call_count == 3


def test_daily_aggregation_executes_three_queries() -> None:
    session = MagicMock(spec=Session)

    run_daily_aggregation(
        session,
        bucket_start=datetime(
            2026,
            9,
            19,
            14,
            37,
            tzinfo=UTC,
        ),
    )

    assert session.execute.call_count == 3


def test_floor_to_hour_normalizes_to_utc_hour() -> None:
    value = datetime(
        2026,
        9,
        19,
        14,
        37,
        42,
        123456,
        tzinfo=UTC,
    )

    assert floor_to_hour(value) == datetime(
        2026,
        9,
        19,
        14,
        0,
        tzinfo=UTC,
    )


def test_floor_to_day_normalizes_to_utc_midnight() -> None:
    value = datetime(
        2026,
        9,
        19,
        14,
        37,
        42,
        123456,
        tzinfo=UTC,
    )

    assert floor_to_day(value) == datetime(
        2026,
        9,
        19,
        0,
        0,
        tzinfo=UTC,
    )


def test_hourly_backfill_processes_each_completed_bucket() -> None:
    session = MagicMock(spec=Session)

    with patch("app.analytics.aggregation.jobs.run_hourly_aggregation") as run_hourly:
        run_hourly_backfill(
            session,
            start_time=datetime(2026, 9, 19, 10, 0, tzinfo=UTC),
            end_time=datetime(2026, 9, 19, 13, 0, tzinfo=UTC),
        )

    assert run_hourly.call_count == 3

    processed_buckets = [call.kwargs["bucket_start"] for call in run_hourly.call_args_list]

    assert processed_buckets == [
        datetime(2026, 9, 19, 10, 0, tzinfo=UTC),
        datetime(2026, 9, 19, 11, 0, tzinfo=UTC),
        datetime(2026, 9, 19, 12, 0, tzinfo=UTC),
    ]


def test_daily_backfill_processes_each_completed_bucket() -> None:
    session = MagicMock(spec=Session)

    with patch("app.analytics.aggregation.jobs.run_daily_aggregation") as run_daily:
        run_daily_backfill(
            session,
            start_time=datetime(2026, 9, 17, 0, 0, tzinfo=UTC),
            end_time=datetime(2026, 9, 20, 0, 0, tzinfo=UTC),
        )

    assert run_daily.call_count == 3

    processed_buckets = [call.kwargs["bucket_start"] for call in run_daily.call_args_list]

    assert processed_buckets == [
        datetime(2026, 9, 17, 0, 0, tzinfo=UTC),
        datetime(2026, 9, 18, 0, 0, tzinfo=UTC),
        datetime(2026, 9, 19, 0, 0, tzinfo=UTC),
    ]


def test_hourly_incremental_refresh_reprocesses_completed_buckets() -> None:
    session = MagicMock(spec=Session)

    with patch("app.analytics.aggregation.jobs.run_hourly_backfill") as run_backfill:
        run_hourly_incremental_refresh(
            session,
            now=datetime(2026, 9, 19, 14, 37, tzinfo=UTC),
            lookback_hours=2,
        )

    run_backfill.assert_called_once_with(
        session,
        start_time=datetime(2026, 9, 19, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 19, 14, 0, tzinfo=UTC),
    )


def test_daily_incremental_refresh_reprocesses_completed_buckets() -> None:
    session = MagicMock(spec=Session)

    with patch("app.analytics.aggregation.jobs.run_daily_backfill") as run_backfill:
        run_daily_incremental_refresh(
            session,
            now=datetime(2026, 9, 19, 14, 37, tzinfo=UTC),
            lookback_days=2,
        )

    run_backfill.assert_called_once_with(
        session,
        start_time=datetime(2026, 9, 17, 0, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 19, 0, 0, tzinfo=UTC),
    )
