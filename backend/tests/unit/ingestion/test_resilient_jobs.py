import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from app.ingestion.resilience import (
    CircuitBreaker,
    CircuitState,
    DeadLetterQueue,
    run_resilient_noaa_job,
    run_resilient_psk_reporter_job,
)


@pytest.mark.asyncio
async def test_noaa_transient_failure_retries_and_succeeds() -> None:
    operation = AsyncMock(
        side_effect=[
            RuntimeError("temporary NOAA failure"),
            6,
        ]
    )

    circuit_breaker = CircuitBreaker()
    dead_letter_queue = DeadLetterQueue()

    with patch(
        "app.ingestion.resilience.asyncio.sleep",
        new_callable=AsyncMock,
    ) as sleep:
        result = await run_resilient_noaa_job(
            operation,
            circuit_breaker=circuit_breaker,
            dead_letter_queue=dead_letter_queue,
        )

    assert result == 6
    assert operation.await_count == 2
    assert sleep.await_count == 1

    assert circuit_breaker.failure_count == 0
    assert circuit_breaker.state is CircuitState.CLOSED
    assert dead_letter_queue.items == ()


@pytest.mark.asyncio
async def test_noaa_terminal_failure_returns_control() -> None:
    operation = AsyncMock(side_effect=RuntimeError("NOAA unavailable"))

    circuit_breaker = CircuitBreaker()
    dead_letter_queue = DeadLetterQueue()

    with patch(
        "app.ingestion.resilience.asyncio.sleep",
        new_callable=AsyncMock,
    ):
        result = await run_resilient_noaa_job(
            operation,
            circuit_breaker=circuit_breaker,
            dead_letter_queue=dead_letter_queue,
        )

    assert result is None
    assert operation.await_count == 3


@pytest.mark.asyncio
async def test_noaa_terminal_failure_creates_dead_letter() -> None:
    operation = AsyncMock(side_effect=RuntimeError("NOAA unavailable"))

    circuit_breaker = CircuitBreaker()
    dead_letter_queue = DeadLetterQueue()

    with patch(
        "app.ingestion.resilience.asyncio.sleep",
        new_callable=AsyncMock,
    ):
        await run_resilient_noaa_job(
            operation,
            circuit_breaker=circuit_breaker,
            dead_letter_queue=dead_letter_queue,
        )

    assert len(dead_letter_queue.items) == 1

    dead_letter = dead_letter_queue.items[0]

    assert dead_letter.provider == "noaa"
    assert dead_letter.operation == "ingestion"
    assert dead_letter.error == "NOAA unavailable"


@pytest.mark.asyncio
async def test_psk_stream_failure_is_captured() -> None:
    operation = AsyncMock(side_effect=RuntimeError("PSK Reporter stream disconnected"))

    circuit_breaker = CircuitBreaker()
    dead_letter_queue = DeadLetterQueue()

    with patch(
        "app.ingestion.resilience.asyncio.sleep",
        new_callable=AsyncMock,
    ):
        await run_resilient_psk_reporter_job(
            operation,
            circuit_breaker=circuit_breaker,
            dead_letter_queue=dead_letter_queue,
        )

    assert operation.await_count == 3

    assert len(dead_letter_queue.items) == 1

    dead_letter = dead_letter_queue.items[0]

    assert dead_letter.provider == "psk_reporter"
    assert dead_letter.operation == "stream"
    assert dead_letter.error == "PSK Reporter stream disconnected"


@pytest.mark.asyncio
async def test_wrapped_job_propagates_cancellation() -> None:
    operation = AsyncMock(side_effect=asyncio.CancelledError)

    circuit_breaker = CircuitBreaker()
    dead_letter_queue = DeadLetterQueue()

    with pytest.raises(asyncio.CancelledError):
        await run_resilient_psk_reporter_job(
            operation,
            circuit_breaker=circuit_breaker,
            dead_letter_queue=dead_letter_queue,
        )

    operation.assert_awaited_once_with()

    assert circuit_breaker.failure_count == 0
    assert dead_letter_queue.items == ()


@pytest.mark.asyncio
async def test_one_provider_failure_does_not_prevent_other_provider() -> None:
    noaa_operation = AsyncMock(side_effect=RuntimeError("NOAA unavailable"))
    psk_operation = AsyncMock(return_value=None)

    noaa_circuit_breaker = CircuitBreaker()
    psk_circuit_breaker = CircuitBreaker()

    dead_letter_queue = DeadLetterQueue()

    with patch(
        "app.ingestion.resilience.asyncio.sleep",
        new_callable=AsyncMock,
    ):
        async with asyncio.TaskGroup() as task_group:
            noaa_task = task_group.create_task(
                run_resilient_noaa_job(
                    noaa_operation,
                    circuit_breaker=noaa_circuit_breaker,
                    dead_letter_queue=dead_letter_queue,
                )
            )

            psk_task = task_group.create_task(
                run_resilient_psk_reporter_job(
                    psk_operation,
                    circuit_breaker=psk_circuit_breaker,
                    dead_letter_queue=dead_letter_queue,
                )
            )

    assert noaa_task.result() is None
    assert psk_task.result() is None

    assert noaa_operation.await_count == 3
    psk_operation.assert_awaited_once_with()

    assert len(dead_letter_queue.items) == 1
    assert dead_letter_queue.items[0].provider == "noaa"

    assert noaa_circuit_breaker.failure_count == 1
    assert psk_circuit_breaker.failure_count == 0
    assert psk_circuit_breaker.state is CircuitState.CLOSED
