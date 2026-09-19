from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.analytics.aggregation.runtime import (
    run_aggregation_runtime,
    run_daily_job,
    run_hourly_job,
)


@pytest.mark.asyncio
async def test_hourly_job_runs_refresh_and_commits() -> None:
    session = MagicMock(spec=Session)

    with (
        patch("app.analytics.aggregation.runtime.create_session") as create_session,
        patch("app.analytics.aggregation.runtime.run_hourly_incremental_refresh") as run_refresh,
    ):
        create_session.return_value.__enter__.return_value = session

        await run_hourly_job()

    run_refresh.assert_called_once()
    assert run_refresh.call_args.args[0] is session
    session.commit.assert_called_once_with()


@pytest.mark.asyncio
async def test_daily_job_runs_refresh_and_commits() -> None:
    session = MagicMock(spec=Session)

    with (
        patch("app.analytics.aggregation.runtime.create_session") as create_session,
        patch("app.analytics.aggregation.runtime.run_daily_incremental_refresh") as run_refresh,
    ):
        create_session.return_value.__enter__.return_value = session

        await run_daily_job()

    run_refresh.assert_called_once()
    assert run_refresh.call_args.args[0] is session
    session.commit.assert_called_once_with()


@pytest.mark.asyncio
async def test_aggregation_runtime_starts_schedules() -> None:
    with patch(
        "app.analytics.aggregation.runtime.run_aggregation_schedules",
        new_callable=AsyncMock,
    ) as run_schedules:
        await run_aggregation_runtime()

    run_schedules.assert_awaited_once_with(
        run_hourly_job,
        run_daily_job,
    )
