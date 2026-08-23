import asyncio
from collections.abc import Awaitable, Callable

NOAA_INTERVAL_SECONDS = 5 * 60


async def run_periodically(
    job: Callable[[], Awaitable[None]],
    interval_seconds: float,
) -> None:
    while True:
        await job()
        await asyncio.sleep(interval_seconds)


async def run_noaa_schedule(
    job: Callable[[], Awaitable[None]],
) -> None:
    await run_periodically(
        job,
        NOAA_INTERVAL_SECONDS,
    )


async def run_psk_reporter_schedule(
    job: Callable[[], Awaitable[None]],
) -> None:
    await job()


async def run_ingestion_schedules(
    noaa_job: Callable[[], Awaitable[None]],
    psk_reporter_job: Callable[[], Awaitable[None]],
) -> None:
    async with asyncio.TaskGroup() as task_group:
        task_group.create_task(run_noaa_schedule(noaa_job))
        task_group.create_task(run_psk_reporter_schedule(psk_reporter_job))
