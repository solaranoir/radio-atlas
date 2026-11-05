import asyncio
from collections.abc import Callable
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.analytics.aggregation.jobs import (
    run_daily_incremental_refresh,
    run_hourly_incremental_refresh,
)
from app.analytics.aggregation.scheduler import run_aggregation_schedules
from app.infrastructure.database.session import create_session
from app.logging.logger import get_logger

logger = get_logger(__name__)


def _run_refresh(
    refresh: Callable[..., None],
    *,
    job_name: str,
) -> None:
    """Run one refresh in its own session; a failure is logged, never raised.

    Aggregation is idempotent and the next scheduled run re-covers the same
    lookback window, so a failed run must not take down the worker (which
    would also stop ingestion running beside it).
    """

    with create_session() as session:
        try:
            refresh(session, now=datetime.now(UTC))
            session.commit()
        except Exception:
            session.rollback()
            logger.error(
                "Aggregation job failed; will retry on next schedule",
                extra={"operation": "aggregation", "job": job_name},
                exc_info=True,
            )


def _hourly(session: Session, *, now: datetime) -> None:
    run_hourly_incremental_refresh(session, now=now)


def _daily(session: Session, *, now: datetime) -> None:
    run_daily_incremental_refresh(session, now=now)


async def run_hourly_job() -> None:
    # Aggregation is blocking SQL that can run for minutes on busy hours; keep
    # it off the event loop so MQTT intake is not starved meanwhile.
    await asyncio.to_thread(_run_refresh, _hourly, job_name="hourly")


async def run_daily_job() -> None:
    await asyncio.to_thread(_run_refresh, _daily, job_name="daily")


async def run_aggregation_runtime() -> None:
    await run_aggregation_schedules(
        run_hourly_job,
        run_daily_job,
    )
