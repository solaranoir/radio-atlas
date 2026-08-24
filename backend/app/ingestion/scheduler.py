import asyncio
from collections.abc import Awaitable, Callable

from app.ingestion.resilience import (
    CircuitBreaker,
    DeadLetterQueue,
    run_resilient_noaa_job,
    run_resilient_psk_reporter_job,
)

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
    noaa_job: Callable[[], Awaitable[int]],
    psk_reporter_job: Callable[[], Awaitable[None]],
) -> None:
    dead_letter_queue = DeadLetterQueue()

    noaa_circuit_breaker = CircuitBreaker()
    psk_circuit_breaker = CircuitBreaker()

    async def resilient_noaa_job() -> None:
        await run_resilient_noaa_job(
            noaa_job,
            circuit_breaker=noaa_circuit_breaker,
            dead_letter_queue=dead_letter_queue,
        )

    async def resilient_psk_reporter_job() -> None:
        await run_resilient_psk_reporter_job(
            psk_reporter_job,
            circuit_breaker=psk_circuit_breaker,
            dead_letter_queue=dead_letter_queue,
        )

    async with asyncio.TaskGroup() as task_group:
        task_group.create_task(run_noaa_schedule(resilient_noaa_job))
        task_group.create_task(run_psk_reporter_schedule(resilient_psk_reporter_job))
