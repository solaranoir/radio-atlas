import asyncio
from collections.abc import Awaitable, Callable

from app.ingestion.resilience import (
    CircuitBreaker,
    CircuitOpenError,
    DeadLetterQueue,
    run_resilient_noaa_job,
    run_resilient_psk_reporter_job,
)
from app.logging.logger import get_logger

logger = get_logger(__name__)

NOAA_INTERVAL_SECONDS = 5 * 60
# The MQTT stream is long-lived; this is only the pause before restarting it
# after it ends or fails. Kept below the circuit breaker's 60-second recovery
# window so an open circuit is retried promptly once it may half-open.
PSK_REPORTER_RESTART_DELAY_SECONDS = 30


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
    *,
    restart_delay_seconds: float = PSK_REPORTER_RESTART_DELAY_SECONDS,
) -> None:
    """Keep the PSK Reporter stream running for the life of the worker.

    The stream only returns when it has stopped, either because it ended or
    because the resilient wrapper absorbed a failure after its retries. Either
    way ingestion must resume; returning would silently end PSK ingestion while
    NOAA keeps the worker alive.
    """

    while True:
        try:
            await job()
            reason = "stream stopped"
        except CircuitOpenError:
            reason = "circuit open"

        logger.error(
            "PSK Reporter ingestion stopped; restarting",
            extra={
                "provider": "psk_reporter",
                "operation": "stream_restart",
                "reason": reason,
                "retry_seconds": restart_delay_seconds,
            },
        )
        await asyncio.sleep(restart_delay_seconds)


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
