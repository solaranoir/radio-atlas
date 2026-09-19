from unittest.mock import AsyncMock, patch

import pytest

from app.analytics.aggregation.scheduler import (
    DAILY_AGGREGATION_INTERVAL_SECONDS,
    HOURLY_AGGREGATION_INTERVAL_SECONDS,
    run_aggregation_schedules,
)


@pytest.mark.asyncio
async def test_aggregation_schedules_start_hourly_and_daily_jobs() -> None:
    hourly_job = AsyncMock()
    daily_job = AsyncMock()

    with patch(
        "app.analytics.aggregation.scheduler.run_periodically",
        new_callable=AsyncMock,
    ) as run_periodically:
        await run_aggregation_schedules(
            hourly_job,
            daily_job,
        )

    assert run_periodically.await_count == 2
    run_periodically.assert_any_await(
        hourly_job,
        HOURLY_AGGREGATION_INTERVAL_SECONDS,
    )
    run_periodically.assert_any_await(
        daily_job,
        DAILY_AGGREGATION_INTERVAL_SECONDS,
    )
