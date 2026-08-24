import asyncio
from collections.abc import Awaitable, Callable
from unittest.mock import AsyncMock, patch

import pytest

from app.ingestion.resilience import CircuitBreaker, DeadLetterQueue
from app.ingestion.scheduler import (
    NOAA_INTERVAL_SECONDS,
    run_ingestion_schedules,
    run_noaa_schedule,
    run_periodically,
    run_psk_reporter_schedule,
)


@pytest.mark.asyncio
async def test_run_periodically_executes_job_immediately() -> None:
    job = AsyncMock()

    with (
        patch(
            "app.ingestion.scheduler.asyncio.sleep",
            new_callable=AsyncMock,
            side_effect=asyncio.CancelledError,
        ) as sleep,
        pytest.raises(asyncio.CancelledError),
    ):
        await run_periodically(
            job,
            interval_seconds=10,
        )

    job.assert_awaited_once_with()
    sleep.assert_awaited_once_with(10)


@pytest.mark.asyncio
async def test_run_periodically_sleeps_between_runs() -> None:
    job = AsyncMock()

    sleep = AsyncMock(
        side_effect=[
            None,
            asyncio.CancelledError(),
        ],
    )

    with (
        patch(
            "app.ingestion.scheduler.asyncio.sleep",
            sleep,
        ),
        pytest.raises(asyncio.CancelledError),
    ):
        await run_periodically(
            job,
            interval_seconds=42,
        )

    assert job.await_count == 2
    assert sleep.await_count == 2

    sleep.assert_any_await(42)


@pytest.mark.asyncio
async def test_noaa_schedule_uses_300_second_interval() -> None:
    job = AsyncMock()

    with patch(
        "app.ingestion.scheduler.run_periodically",
        new_callable=AsyncMock,
    ) as run_periodically_mock:
        await run_noaa_schedule(job)

    run_periodically_mock.assert_awaited_once_with(
        job,
        NOAA_INTERVAL_SECONDS,
    )

    assert NOAA_INTERVAL_SECONDS == 300


@pytest.mark.asyncio
async def test_psk_reporter_schedule_invokes_stream_once() -> None:
    job = AsyncMock()

    await run_psk_reporter_schedule(job)

    job.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_combined_scheduler_starts_both_jobs_concurrently() -> None:
    noaa_job = AsyncMock()
    psk_reporter_job = AsyncMock()

    noaa_started = asyncio.Event()
    psk_started = asyncio.Event()

    async def noaa_schedule(
        job: Callable[[], Awaitable[None]],
    ) -> None:
        noaa_started.set()
        await psk_started.wait()

    async def psk_schedule(
        job: Callable[[], Awaitable[None]],
    ) -> None:
        psk_started.set()
        await noaa_started.wait()

    with (
        patch(
            "app.ingestion.scheduler.run_noaa_schedule",
            side_effect=noaa_schedule,
        ) as run_noaa,
        patch(
            "app.ingestion.scheduler.run_psk_reporter_schedule",
            side_effect=psk_schedule,
        ) as run_psk,
    ):
        await run_ingestion_schedules(
            noaa_job,
            psk_reporter_job,
        )

    run_noaa.assert_awaited_once()
    run_psk.assert_awaited_once()

    assert noaa_started.is_set()
    assert psk_started.is_set()


@pytest.mark.asyncio
async def test_scheduler_propagates_cancellation() -> None:
    job = AsyncMock(
        side_effect=asyncio.CancelledError,
    )

    with pytest.raises(asyncio.CancelledError):
        await run_periodically(
            job,
            interval_seconds=300,
        )

    job.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_ingestion_schedules_wraps_noaa_with_resilience() -> None:
    noaa_job = AsyncMock(return_value=5)
    psk_reporter_job = AsyncMock()

    async def invoke_job(
        job: Callable[[], Awaitable[None]],
    ) -> None:
        await job()

    with (
        patch(
            "app.ingestion.scheduler.run_resilient_noaa_job",
            new_callable=AsyncMock,
        ) as resilient_noaa,
        patch(
            "app.ingestion.scheduler.run_resilient_psk_reporter_job",
            new_callable=AsyncMock,
        ),
        patch(
            "app.ingestion.scheduler.run_noaa_schedule",
            side_effect=invoke_job,
        ),
        patch(
            "app.ingestion.scheduler.run_psk_reporter_schedule",
            new_callable=AsyncMock,
        ),
    ):
        await run_ingestion_schedules(
            noaa_job,
            psk_reporter_job,
        )

    resilient_noaa.assert_awaited_once()

    call = resilient_noaa.await_args

    assert call is not None
    assert call.args[0] is noaa_job
    assert isinstance(
        call.kwargs["circuit_breaker"],
        CircuitBreaker,
    )
    assert isinstance(
        call.kwargs["dead_letter_queue"],
        DeadLetterQueue,
    )


@pytest.mark.asyncio
async def test_ingestion_schedules_wraps_psk_reporter_with_resilience() -> None:
    noaa_job = AsyncMock(return_value=5)
    psk_reporter_job = AsyncMock()

    async def invoke_job(
        job: Callable[[], Awaitable[None]],
    ) -> None:
        await job()

    with (
        patch(
            "app.ingestion.scheduler.run_resilient_noaa_job",
            new_callable=AsyncMock,
        ),
        patch(
            "app.ingestion.scheduler.run_resilient_psk_reporter_job",
            new_callable=AsyncMock,
        ) as resilient_psk,
        patch(
            "app.ingestion.scheduler.run_noaa_schedule",
            new_callable=AsyncMock,
        ),
        patch(
            "app.ingestion.scheduler.run_psk_reporter_schedule",
            side_effect=invoke_job,
        ),
    ):
        await run_ingestion_schedules(
            noaa_job,
            psk_reporter_job,
        )

    resilient_psk.assert_awaited_once()

    call = resilient_psk.await_args

    resilient_psk.assert_awaited_once()

    call = resilient_psk.await_args

    assert call is not None
    assert call.args[0] is psk_reporter_job
    assert isinstance(
        call.kwargs["circuit_breaker"],
        CircuitBreaker,
    )
    assert isinstance(
        call.kwargs["dead_letter_queue"],
        DeadLetterQueue,
    )


@pytest.mark.asyncio
async def test_resilient_branch_return_does_not_prevent_other_scheduler_from_starting() -> None:
    noaa_job = AsyncMock(return_value=5)
    psk_reporter_job = AsyncMock()

    noaa_started = asyncio.Event()
    psk_started = asyncio.Event()

    async def noaa_schedule(
        job: Callable[[], Awaitable[None]],
    ) -> None:
        noaa_started.set()
        await job()

    async def psk_schedule(
        job: Callable[[], Awaitable[None]],
    ) -> None:
        psk_started.set()
        await noaa_started.wait()
        await job()

    with (
        patch(
            "app.ingestion.scheduler.run_resilient_noaa_job",
            new_callable=AsyncMock,
            return_value=None,
        ) as resilient_noaa,
        patch(
            "app.ingestion.scheduler.run_resilient_psk_reporter_job",
            new_callable=AsyncMock,
            return_value=None,
        ) as resilient_psk,
        patch(
            "app.ingestion.scheduler.run_noaa_schedule",
            side_effect=noaa_schedule,
        ),
        patch(
            "app.ingestion.scheduler.run_psk_reporter_schedule",
            side_effect=psk_schedule,
        ),
    ):
        await run_ingestion_schedules(
            noaa_job,
            psk_reporter_job,
        )

    assert noaa_started.is_set()
    assert psk_started.is_set()

    resilient_noaa.assert_awaited_once()
    resilient_psk.assert_awaited_once()
