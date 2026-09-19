import asyncio
from collections.abc import Awaitable, Callable

HOURLY_AGGREGATION_INTERVAL_SECONDS = 60 * 60
DAILY_AGGREGATION_INTERVAL_SECONDS = 24 * 60 * 60


async def run_periodically(
    job: Callable[[], Awaitable[None]],
    interval_seconds: float,
) -> None:
    while True:
        await job()
        await asyncio.sleep(interval_seconds)


async def run_aggregation_schedules(
    hourly_job: Callable[[], Awaitable[None]],
    daily_job: Callable[[], Awaitable[None]],
) -> None:
    async with asyncio.TaskGroup() as task_group:
        task_group.create_task(
            run_periodically(
                hourly_job,
                HOURLY_AGGREGATION_INTERVAL_SECONDS,
            )
        )
        task_group.create_task(
            run_periodically(
                daily_job,
                DAILY_AGGREGATION_INTERVAL_SECONDS,
            )
        )
