"""Regression: busy hours exceeded PostgreSQL's 65,535 bind-parameter limit.

Production (2026-11-01) crash-looped the worker with
``psycopg.OperationalError: sending query and params failed: number of
parameters must be between 0 and 65535`` when an hour had thousands of
active stations.
"""

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.analytics.aggregation.persistence import upsert_station_rollups
from app.infrastructure.database.models import AnalyticsStationHourly

BUCKET = datetime(2031, 4, 1, 12, tzinfo=UTC)
STATION_COUNT = 7_000  # 7,000 rows x 10 columns = 70,000 parameters


def _rows(observation_count: int) -> list[dict[str, object]]:
    return [
        {
            "bucket_start": BUCKET,
            "station_id": None,
            "callsign": f"BL{index:05d}",
            "observation_count": observation_count,
            "unique_counterparty_count": 1,
            "snr_sample_count": 1,
            "snr_min_db": -10,
            "snr_max_db": -10,
            "snr_avg_db": -10.0,
        }
        for index in range(STATION_COUNT)
    ]


def _stored(session: Session) -> tuple[int, int]:
    count, total = session.execute(
        select(
            func.count(AnalyticsStationHourly.id),
            func.sum(AnalyticsStationHourly.observation_count),
        ).where(AnalyticsStationHourly.bucket_start == BUCKET)
    ).one()
    return count, total


def test_station_upsert_beyond_bind_parameter_limit(db_session: Session) -> None:
    upsert_station_rollups(
        db_session, model=AnalyticsStationHourly, rows=_rows(1), direction="receiver"
    )
    db_session.flush()
    assert _stored(db_session) == (STATION_COUNT, STATION_COUNT)

    # Re-running the same hour (incremental refresh) updates rather than duplicates.
    upsert_station_rollups(
        db_session, model=AnalyticsStationHourly, rows=_rows(2), direction="receiver"
    )
    db_session.flush()
    db_session.expire_all()
    assert _stored(db_session) == (STATION_COUNT, 2 * STATION_COUNT)
