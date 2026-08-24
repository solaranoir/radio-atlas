import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum


@dataclass(frozen=True)
class DeadLetter:
    provider: str
    operation: str
    error: str
    failed_at: datetime


class CircuitState(StrEnum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenError(RuntimeError):
    """Raised when an ingestion circuit is open."""


class CircuitBreaker:
    def __init__(
        self,
        *,
        failure_threshold: int = 3,
        recovery_timeout_seconds: float = 60.0,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.opened_at: datetime | None = None

    def record_success(self) -> None:
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.opened_at = None

    def record_failure(self) -> None:
        self.failure_count += 1

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.opened_at = datetime.now(UTC)

    def allow_request(self) -> None:
        if self.state is not CircuitState.OPEN:
            return

        if self.opened_at is None:
            raise CircuitOpenError("Circuit is open")

        recovery_at = self.opened_at + timedelta(
            seconds=self.recovery_timeout_seconds,
        )

        if datetime.now(UTC) < recovery_at:
            raise CircuitOpenError("Circuit is open")

        self.state = CircuitState.HALF_OPEN


async def retry_async[T](
    operation: Callable[[], Awaitable[T]],
    *,
    attempts: int = 3,
    delay_seconds: float = 1.0,
) -> T:
    if attempts < 1:
        raise ValueError("attempts must be at least 1")

    for attempt in range(attempts):
        try:
            return await operation()
        except asyncio.CancelledError:
            raise
        except Exception:
            if attempt == attempts - 1:
                raise

            await asyncio.sleep(delay_seconds)

    raise RuntimeError("unreachable")


class DeadLetterQueue:
    def __init__(self) -> None:
        self._items: list[DeadLetter] = []

    def add(
        self,
        *,
        provider: str,
        operation: str,
        error: Exception,
    ) -> None:
        self._items.append(
            DeadLetter(
                provider=provider,
                operation=operation,
                error=str(error),
                failed_at=datetime.now(UTC),
            )
        )

    @property
    def items(self) -> tuple[DeadLetter, ...]:
        return tuple(self._items)


async def run_resilient_job[T](
    operation: Callable[[], Awaitable[T]],
    *,
    provider: str,
    operation_name: str,
    circuit_breaker: CircuitBreaker,
    dead_letter_queue: DeadLetterQueue,
    attempts: int = 3,
    delay_seconds: float = 1.0,
) -> T | None:
    circuit_breaker.allow_request()

    try:
        result = await retry_async(
            operation,
            attempts=attempts,
            delay_seconds=delay_seconds,
        )
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        circuit_breaker.record_failure()

        dead_letter_queue.add(
            provider=provider,
            operation=operation_name,
            error=exc,
        )

        return None

    circuit_breaker.record_success()

    return result


async def run_resilient_noaa_job(
    operation: Callable[[], Awaitable[int]],
    *,
    circuit_breaker: CircuitBreaker,
    dead_letter_queue: DeadLetterQueue,
) -> int | None:
    return await run_resilient_job(
        operation,
        provider="noaa",
        operation_name="ingestion",
        circuit_breaker=circuit_breaker,
        dead_letter_queue=dead_letter_queue,
    )


async def run_resilient_psk_reporter_job(
    operation: Callable[[], Awaitable[None]],
    *,
    circuit_breaker: CircuitBreaker,
    dead_letter_queue: DeadLetterQueue,
) -> None:
    await run_resilient_job(
        operation,
        provider="psk_reporter",
        operation_name="stream",
        circuit_breaker=circuit_breaker,
        dead_letter_queue=dead_letter_queue,
    )
