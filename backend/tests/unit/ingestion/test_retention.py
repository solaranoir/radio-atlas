import asyncio
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.ingestion.retention import (
    RetentionResult,
    delete_spots_between,
    retention_cutoff,
    run_retention_job,
    run_retention_runtime,
    run_spot_retention,
)

NOW = datetime(2026, 11, 4, 17, 45, tzinfo=UTC)


def test_cutoff_is_start_of_day_retention_days_ago() -> None:
    assert retention_cutoff(NOW, 14) == datetime(2026, 10, 21, tzinfo=UTC)


def test_rejects_non_positive_arguments() -> None:
    session = MagicMock(spec=Session)

    with pytest.raises(ValueError):
        run_spot_retention(session, now=NOW, retention_days=0)
    with pytest.raises(ValueError):
        delete_spots_between(session, start_time=NOW, end_time=NOW, batch_size=0)


def test_job_logs_and_swallows_failures() -> None:
    session = MagicMock(spec=Session)

    with (
        patch("app.ingestion.retention.create_session") as create_session,
        patch("app.ingestion.retention.run_spot_retention", side_effect=RuntimeError("boom")),
        patch("app.ingestion.retention.logger") as logger,
    ):
        create_session.return_value.__enter__.return_value = session

        run_retention_job(14)

    session.rollback.assert_called_once_with()
    logger.error.assert_called_once()


def test_job_logs_completion() -> None:
    result = RetentionResult(cutoff=NOW, days_processed=2, spots_deleted=10)

    with (
        patch("app.ingestion.retention.create_session"),
        patch("app.ingestion.retention.run_spot_retention", return_value=result) as run,
        patch("app.ingestion.retention.logger") as logger,
    ):
        run_retention_job(7)

    assert run.call_args.kwargs["retention_days"] == 7
    extra = logger.info.call_args.kwargs["extra"]
    assert extra["days_processed"] == 2
    assert extra["record_count"] == 10


@pytest.mark.asyncio
async def test_runtime_waits_then_runs_repeatedly_in_a_thread() -> None:
    sleep = AsyncMock(side_effect=[None, None, asyncio.CancelledError()])

    with (
        patch("app.ingestion.retention.asyncio.sleep", sleep),
        patch("app.ingestion.retention.run_retention_job") as job,
        pytest.raises(asyncio.CancelledError),
    ):
        await run_retention_runtime(14, initial_delay_seconds=5, interval_seconds=60)

    assert job.call_count == 2
    job.assert_called_with(14)
    assert [call.args[0] for call in sleep.await_args_list] == [5, 60, 60]
