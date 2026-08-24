import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from app.ingestion.resilience import (
    CircuitBreaker,
    CircuitOpenError,
    CircuitState,
    DeadLetterQueue,
    retry_async,
    run_resilient_job,
)


@pytest.mark.asyncio
async def test_retry_succeeds_on_first_attempt() -> None:
    operation = AsyncMock(return_value="ok")

    result = await retry_async(operation)

    assert result == "ok"
    operation.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_retry_succeeds_after_transient_failures() -> None:
    operation = AsyncMock(
        side_effect=[
            RuntimeError("first failure"),
            RuntimeError("second failure"),
            "ok",
        ]
    )

    with patch(
        "app.ingestion.resilience.asyncio.sleep",
        new_callable=AsyncMock,
    ) as sleep:
        result = await retry_async(
            operation,
            attempts=3,
            delay_seconds=2,
        )

    assert result == "ok"
    assert operation.await_count == 3
    assert sleep.await_count == 2
    sleep.assert_any_await(2)


@pytest.mark.asyncio
async def test_retry_raises_after_max_attempts() -> None:
    operation = AsyncMock(side_effect=RuntimeError("still failing"))

    with (
        patch(
            "app.ingestion.resilience.asyncio.sleep",
            new_callable=AsyncMock,
        ) as sleep,
        pytest.raises(
            RuntimeError,
            match="still failing",
        ),
    ):
        await retry_async(
            operation,
            attempts=3,
            delay_seconds=1,
        )

    assert operation.await_count == 3
    assert sleep.await_count == 2


@pytest.mark.asyncio
async def test_retry_propagates_cancellation() -> None:
    operation = AsyncMock(side_effect=asyncio.CancelledError)

    with (
        patch(
            "app.ingestion.resilience.asyncio.sleep",
            new_callable=AsyncMock,
        ) as sleep,
        pytest.raises(asyncio.CancelledError),
    ):
        await retry_async(
            operation,
            attempts=3,
        )

    operation.assert_awaited_once_with()
    sleep.assert_not_awaited()


def test_circuit_opens_after_failure_threshold() -> None:
    circuit_breaker = CircuitBreaker(
        failure_threshold=3,
    )

    circuit_breaker.record_failure()
    circuit_breaker.record_failure()

    assert circuit_breaker.state.value == "closed"
    assert circuit_breaker.failure_count == 2

    circuit_breaker.record_failure()

    assert circuit_breaker.state is CircuitState.OPEN
    assert circuit_breaker.failure_count == 3


def test_success_resets_circuit() -> None:
    circuit_breaker = CircuitBreaker(
        failure_threshold=3,
    )

    circuit_breaker.record_failure()
    circuit_breaker.record_failure()

    circuit_breaker.record_success()

    assert circuit_breaker.state is CircuitState.CLOSED
    assert circuit_breaker.failure_count == 0


def test_open_circuit_blocks_work() -> None:
    circuit_breaker = CircuitBreaker(
        failure_threshold=1,
    )

    circuit_breaker.record_failure()

    with pytest.raises(
        CircuitOpenError,
        match="Circuit is open",
    ):
        circuit_breaker.allow_request()


@pytest.mark.asyncio
async def test_failed_resilient_job_creates_dead_letter() -> None:
    operation = AsyncMock(side_effect=RuntimeError("NOAA unavailable"))

    circuit_breaker = CircuitBreaker()
    dead_letter_queue = DeadLetterQueue()

    result = await run_resilient_job(
        operation,
        provider="noaa",
        operation_name="fetch",
        circuit_breaker=circuit_breaker,
        dead_letter_queue=dead_letter_queue,
        attempts=1,
    )

    assert result is None
    assert len(dead_letter_queue.items) == 1

    dead_letter = dead_letter_queue.items[0]

    assert dead_letter.provider == "noaa"
    assert dead_letter.operation == "fetch"
    assert dead_letter.error == "NOAA unavailable"


@pytest.mark.asyncio
async def test_successful_resilient_job_does_not_create_dead_letter() -> None:
    operation = AsyncMock(return_value=5)

    circuit_breaker = CircuitBreaker()
    dead_letter_queue = DeadLetterQueue()

    result = await run_resilient_job(
        operation,
        provider="noaa",
        operation_name="fetch",
        circuit_breaker=circuit_breaker,
        dead_letter_queue=dead_letter_queue,
        attempts=1,
    )

    assert result == 5
    assert dead_letter_queue.items == ()
    assert circuit_breaker.state is CircuitState.CLOSED
    assert circuit_breaker.failure_count == 0


@pytest.mark.asyncio
async def test_failed_resilient_job_returns_none_instead_of_raising() -> None:
    operation = AsyncMock(side_effect=RuntimeError("provider exploded"))

    circuit_breaker = CircuitBreaker()
    dead_letter_queue = DeadLetterQueue()

    result = await run_resilient_job(
        operation,
        provider="psk_reporter",
        operation_name="stream",
        circuit_breaker=circuit_breaker,
        dead_letter_queue=dead_letter_queue,
        attempts=1,
    )

    assert result is None
    assert circuit_breaker.failure_count == 1


@pytest.mark.asyncio
async def test_resilient_job_propagates_cancellation() -> None:
    operation = AsyncMock(side_effect=asyncio.CancelledError)

    circuit_breaker = CircuitBreaker()
    dead_letter_queue = DeadLetterQueue()

    with pytest.raises(asyncio.CancelledError):
        await run_resilient_job(
            operation,
            provider="psk_reporter",
            operation_name="stream",
            circuit_breaker=circuit_breaker,
            dead_letter_queue=dead_letter_queue,
            attempts=3,
        )

    assert circuit_breaker.failure_count == 0
    assert dead_letter_queue.items == ()


@pytest.mark.asyncio
async def test_open_circuit_prevents_operation_from_running() -> None:
    operation = AsyncMock(return_value="should not run")

    circuit_breaker = CircuitBreaker(
        failure_threshold=1,
    )
    circuit_breaker.record_failure()

    dead_letter_queue = DeadLetterQueue()

    with pytest.raises(
        CircuitOpenError,
        match="Circuit is open",
    ):
        await run_resilient_job(
            operation,
            provider="noaa",
            operation_name="fetch",
            circuit_breaker=circuit_breaker,
            dead_letter_queue=dead_letter_queue,
        )

    operation.assert_not_awaited()


def test_open_circuit_stays_blocked_during_cooldown() -> None:
    circuit_breaker = CircuitBreaker(
        failure_threshold=1,
        recovery_timeout_seconds=60,
    )

    circuit_breaker.record_failure()

    assert circuit_breaker.state is CircuitState.OPEN

    with pytest.raises(
        CircuitOpenError,
        match="Circuit is open",
    ):
        circuit_breaker.allow_request()

    assert circuit_breaker.state is CircuitState.OPEN


def test_open_circuit_becomes_half_open_after_cooldown() -> None:
    circuit_breaker = CircuitBreaker(
        failure_threshold=1,
        recovery_timeout_seconds=0,
    )

    circuit_breaker.record_failure()

    assert circuit_breaker.state.value == "open"

    circuit_breaker.allow_request()

    assert circuit_breaker.state is CircuitState.HALF_OPEN


def test_successful_half_open_request_closes_circuit() -> None:
    circuit_breaker = CircuitBreaker(
        failure_threshold=1,
        recovery_timeout_seconds=0,
    )

    circuit_breaker.record_failure()
    circuit_breaker.allow_request()

    assert circuit_breaker.state.value == "half_open"

    circuit_breaker.record_success()

    assert circuit_breaker.state is CircuitState.CLOSED
    assert circuit_breaker.failure_count == 0
    assert circuit_breaker.opened_at is None


@pytest.mark.asyncio
async def test_retry_rejects_invalid_attempt_count() -> None:
    operation = AsyncMock()

    with pytest.raises(
        ValueError,
        match="attempts must be at least 1",
    ):
        await retry_async(
            operation,
            attempts=0,
        )

    operation.assert_not_awaited()
