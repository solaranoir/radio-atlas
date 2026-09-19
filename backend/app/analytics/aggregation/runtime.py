from datetime import UTC, datetime

from app.analytics.aggregation.jobs import (
    run_daily_incremental_refresh,
    run_hourly_incremental_refresh,
)
from app.analytics.aggregation.scheduler import run_aggregation_schedules
from app.infrastructure.database.session import create_session


async def run_hourly_job() -> None:
    with create_session() as session:
        run_hourly_incremental_refresh(
            session,
            now=datetime.now(UTC),
        )
        session.commit()


async def run_daily_job() -> None:
    with create_session() as session:
        run_daily_incremental_refresh(
            session,
            now=datetime.now(UTC),
        )
        session.commit()

async def run_aggregation_runtime() -> None:
    await run_aggregation_schedules(
        run_hourly_job,
        run_daily_job,
    )
