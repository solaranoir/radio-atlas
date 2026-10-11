import asyncio
from collections import OrderedDict
from contextlib import suppress
from time import perf_counter

from sqlalchemy.orm import Session

from app.domain import SpotObservation
from app.health import psk_reporter_health
from app.ingestion.persistence import persist_spot_batch
from app.logging.logger import get_logger
from app.observations.deduplication import observation_key
from app.observations.normalizer import normalize_observation
from app.providers.psk_reporter import PSKReporterProvider

logger = get_logger(__name__)


async def run_psk_reporter_ingestion(
    session: Session,
    provider: PSKReporterProvider,
    *,
    batch_size: int = 100,
    flush_seconds: float = 1.0,
) -> None:
    if batch_size < 1 or flush_seconds <= 0:
        raise ValueError("Batch size and flush interval must be positive")
    seen: OrderedDict[object, None] = OrderedDict()
    batch: list[SpotObservation] = []
    stream = provider.stream()
    pending = None
    deadline = 0.0

    def write_batch(items: list[SpotObservation]) -> None:
        try:
            persist_spot_batch(session, items)
            session.commit()
        except Exception:
            session.rollback()
            raise

    async def flush() -> None:
        if not batch:
            return
        started = perf_counter()
        # Shield and join the write on cancellation before closing or reusing its session.
        write = asyncio.create_task(asyncio.to_thread(write_batch, list(batch)))
        try:
            await asyncio.shield(write)
        except asyncio.CancelledError:
            await write
            batch.clear()
            raise
        except Exception:
            batch.clear()
            raise
        logger.info(
            "PSK Reporter batch persisted",
            extra={
                "record_count": len(batch),
                "duration_ms": round((perf_counter() - started) * 1000, 2),
            },
        )
        batch.clear()
        psk_reporter_health.record_success()

    try:
        while True:
            if pending is None:
                pending = asyncio.create_task(anext(stream))
            timeout = max(0, deadline - asyncio.get_running_loop().time()) if batch else None
            done, _ = await asyncio.wait({pending}, timeout=timeout)
            if not done:
                await flush()
                continue
            try:
                raw = pending.result()
            except StopAsyncIteration:
                pending = None
                break
            pending = None
            observation = normalize_observation(raw)
            if not isinstance(observation, SpotObservation):
                raise TypeError("PSK Reporter must emit spot observations")
            key = observation_key(observation)
            if key in seen:
                continue
            seen[key] = None
            if len(seen) > 100_000:
                seen.popitem(last=False)
            if not batch:
                deadline = asyncio.get_running_loop().time() + flush_seconds
            batch.append(observation)
            if len(batch) >= batch_size:
                await flush()
        await flush()
    except (asyncio.CancelledError, Exception):
        await flush()
        raise
    finally:
        if pending is not None:
            pending.cancel()
            with suppress(asyncio.CancelledError, StopAsyncIteration):
                await pending
        await stream.aclose()
