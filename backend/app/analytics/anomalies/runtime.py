from collections.abc import Callable
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.analytics.aggregation.jobs import floor_to_day
from app.analytics.anomalies.config import DEFAULT_BASELINE_CONFIG, BaselineConfig
from app.analytics.anomalies.service import refresh_baselines
from app.infrastructure.database.session import create_session
from app.logging.logger import get_logger

logger = get_logger(__name__)


def run_baseline_refresh(
    *,
    now: datetime | None = None,
    config: BaselineConfig = DEFAULT_BASELINE_CONFIG,
    session_factory: Callable[[], Session] = create_session,
) -> None:
    """Refresh stored baselines as of the start of the current UTC day.

    Runs after the daily rollup refresh so yesterday's daily rollups exist.
    A failure is logged, never raised: baselines are derived data and the
    next daily run rebuilds them from scratch.
    """

    as_of = floor_to_day(now or datetime.now(UTC))
    with session_factory() as session:
        try:
            result = refresh_baselines(session, as_of=as_of, config=config)
            session.commit()
        except Exception:
            session.rollback()
            logger.error(
                "Baseline refresh failed; will retry on next schedule",
                extra={"operation": "baselines", "as_of": as_of.isoformat()},
                exc_info=True,
            )
            return

    logger.info(
        "Baselines refreshed",
        extra={
            "operation": "baselines",
            "baseline_version": result.baseline_version,
            "as_of": as_of.isoformat(),
            "snapshots": result.snapshot_count,
            "band_dimensions": result.band_dimensions,
            "station_dimensions": result.station_dimensions,
            "pruned_rows": result.pruned_rows,
            **{f"quality_{k}": v for k, v in result.quality_totals().items()},
        },
    )
