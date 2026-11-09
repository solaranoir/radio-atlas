"""Raw spot retention: roll up, then delete spots older than the retention window.

Raw spots dominate storage (~270 bytes each including indexes) and arrive at
tens to hundreds per second, so they cannot be kept indefinitely. Analytics,
the timeline and anomaly detection read hourly/daily rollups, which are tiny
and kept forever. Replay of raw spots is limited to the retention window.

Each expired UTC day is processed oldest-first as a self-contained unit:

1. Rebuild that day's hourly and daily rollups from its raw spots and record
   the day in ``spot_retention_days``, in one transaction. This also repairs
   hours an earlier aggregation run missed (for example during a crash)
   before their source data is gone.
2. Delete the day's spots in bounded batches, committing each batch to keep
   transactions, locks and WAL bursts small.

A day is rolled up at most once. An interrupted run resumes by deleting the
remaining spots of an already-marked day without re-aggregating it. Spots
arriving more than the retention window late for a marked day are deleted
without being counted; PSK Reporter spots arrive in real time, so this is a
documented edge rather than an expected loss.
"""

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, cast

from sqlalchemy import CursorResult, delete, func, select
from sqlalchemy.orm import Session

from app.analytics.aggregation.jobs import (
    floor_to_day,
    run_daily_aggregation,
    run_hourly_backfill,
)
from app.infrastructure.database.models import Spot, SpotRetentionDay
from app.infrastructure.database.session import create_session
from app.logging.logger import get_logger

logger = get_logger(__name__)

DEFAULT_DELETE_BATCH_SIZE = 10_000
# Hourly so an expired day is removed soon after midnight UTC, not up to a day later.
RETENTION_INTERVAL_SECONDS = 60 * 60
# Let ingestion and the first aggregation pass settle after a (re)start.
RETENTION_INITIAL_DELAY_SECONDS = 5 * 60


@dataclass(frozen=True)
class RetentionResult:
    cutoff: datetime
    days_processed: int
    spots_deleted: int


def retention_cutoff(now: datetime, retention_days: int) -> datetime:
    """Start of the oldest UTC day that is kept in full."""

    return floor_to_day(now) - timedelta(days=retention_days)


def oldest_spot_time(
    session: Session,
    *,
    at_or_after: datetime | None = None,
) -> datetime | None:
    query = select(func.min(Spot.observed_at))
    if at_or_after is not None:
        query = query.where(Spot.observed_at >= at_or_after)
    return session.execute(query).scalar_one_or_none()


def roll_up_day_once(session: Session, day_start: datetime) -> bool:
    """Rebuild a day's rollups unless already done; returns True if rebuilt.

    The marker row is added in the same transaction as the rollups, so a day
    is either fully rolled up and marked, or neither. Once marked, the day is
    never re-aggregated: its raw spots may already be partly deleted, and
    recomputing would overwrite the rollups with lower counts.
    """

    if session.get(SpotRetentionDay, day_start) is not None:
        return False
    day_end = day_start + timedelta(days=1)
    run_hourly_backfill(session, start_time=day_start, end_time=day_end)
    run_daily_aggregation(session, bucket_start=day_start)
    session.add(SpotRetentionDay(day_start=day_start))
    return True


def delete_spots_between(
    session: Session,
    *,
    start_time: datetime,
    end_time: datetime,
    batch_size: int = DEFAULT_DELETE_BATCH_SIZE,
) -> int:
    """Delete spots observed in [start_time, end_time) in committed batches.

    Bounded on both sides so a late-arriving spot for an earlier day, which
    has not been rolled up yet, is left for the next run rather than lost.
    """

    if batch_size < 1:
        raise ValueError("batch_size must be positive")

    deleted = 0
    while True:
        batch = (
            select(Spot.id)
            .where(Spot.observed_at >= start_time, Spot.observed_at < end_time)
            .limit(batch_size)
        )
        result = cast(
            CursorResult[Any],
            session.execute(
                delete(Spot).where(Spot.id.in_(batch)).execution_options(synchronize_session=False)
            ),
        )
        session.commit()
        count = result.rowcount or 0
        deleted += count
        if count < batch_size:
            return deleted


def run_spot_retention(
    session: Session,
    *,
    now: datetime,
    retention_days: int,
    batch_size: int = DEFAULT_DELETE_BATCH_SIZE,
) -> RetentionResult:
    if retention_days < 1:
        raise ValueError("retention_days must be positive")

    cutoff = retention_cutoff(now, retention_days)
    days_processed = 0
    spots_deleted = 0

    oldest = oldest_spot_time(session)

    while oldest is not None and (day_start := floor_to_day(oldest)) < cutoff:
        rolled_up = roll_up_day_once(session, day_start)
        session.commit()

        day_end = day_start + timedelta(days=1)
        deleted = delete_spots_between(
            session, start_time=day_start, end_time=day_end, batch_size=batch_size
        )
        days_processed += 1
        spots_deleted += deleted

        logger.info(
            "Spot retention day processed",
            extra={
                "operation": "retention",
                "day": day_start.date().isoformat(),
                "rolled_up": rolled_up,
                "record_count": deleted,
            },
        )
        # Jump to the next day that has spots; history can have long gaps.
        oldest = oldest_spot_time(session, at_or_after=day_end)

    return RetentionResult(
        cutoff=cutoff,
        days_processed=days_processed,
        spots_deleted=spots_deleted,
    )


def run_retention_job(retention_days: int) -> None:
    """One scheduled retention pass; failures are logged, never raised."""

    with create_session() as session:
        try:
            result = run_spot_retention(
                session,
                now=datetime.now(UTC),
                retention_days=retention_days,
            )
        except Exception:
            session.rollback()
            logger.error(
                "Spot retention failed; will retry on next schedule",
                extra={"operation": "retention"},
                exc_info=True,
            )
            return

    logger.info(
        "Spot retention completed",
        extra={
            "operation": "retention",
            "cutoff": result.cutoff.isoformat(),
            "days_processed": result.days_processed,
            "record_count": result.spots_deleted,
        },
    )


async def run_retention_runtime(
    retention_days: int,
    *,
    initial_delay_seconds: float = RETENTION_INITIAL_DELAY_SECONDS,
    interval_seconds: float = RETENTION_INTERVAL_SECONDS,
) -> None:
    await asyncio.sleep(initial_delay_seconds)
    while True:
        # Blocking SQL; keep it off the event loop that serves MQTT intake.
        await asyncio.to_thread(run_retention_job, retention_days)
        await asyncio.sleep(interval_seconds)
