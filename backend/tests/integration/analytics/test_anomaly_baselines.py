from dataclasses import replace
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from sqlalchemy import func, insert, select
from sqlalchemy.orm import Session

from app.analytics.anomalies.config import DEFAULT_BASELINE_CONFIG
from app.analytics.anomalies.persistence import load_coverage
from app.analytics.anomalies.service import refresh_baselines
from app.infrastructure.database.models import (
    AnalyticsBandDaily,
    AnalyticsBandHourly,
    AnalyticsStationDaily,
    AnalyticsStationHourly,
    AnomalyBaseline,
)

# Far from any real data so existing local rows cannot leak into windows.
AS_OF = datetime(2031, 6, 2, tzinfo=UTC)
DAYS = 30
CONFIG = replace(DEFAULT_BASELINE_CONFIG, station_limit=2)
SLOTS = 24 + 7


def _band_row(bucket: datetime, band: str, count: int) -> dict[str, Any]:
    return {
        "bucket_start": bucket,
        "band": band,
        "mode": "FT8",
        "observation_count": count,
        "unique_sender_count": max(count // 4, 1),
        "unique_receiver_count": max(count // 6, 1),
        "snr_sample_count": count,
        "snr_min_db": -20,
        "snr_max_db": 5,
        "snr_avg_db": -9.5,
    }


def _station_row(bucket: datetime, callsign: str, count: int) -> dict[str, Any]:
    return {
        "bucket_start": bucket,
        "station_id": None,
        "callsign": callsign,
        "direction": "receiver",
        "observation_count": count,
        "unique_counterparty_count": max(count // 3, 1),
        "snr_sample_count": count,
        "snr_min_db": -20,
        "snr_max_db": 5,
        "snr_avg_db": -11.0,
    }


@pytest.fixture
def seeded(db_session: Session) -> Session:
    hours = [AS_OF - timedelta(hours=n) for n in range(1, DAYS * 24 + 1)]
    days = [AS_OF - timedelta(days=n) for n in range(1, DAYS + 1)]
    stations = {"BIG1": 400, "MID2": 120, "LOW3": 5}

    def busy(bucket: datetime) -> int:
        return 300 + 200 * (bucket.hour in range(12, 20)) + bucket.day % 7

    db_session.execute(
        insert(AnalyticsBandHourly),
        [_band_row(h, "20m", busy(h)) for h in hours]
        + [_band_row(h, "10m", 2) for h in hours[::5]],
    )
    db_session.execute(
        insert(AnalyticsBandDaily),
        [_band_row(d, "20m", 9_000 + d.day) for d in days],
    )
    db_session.execute(
        insert(AnalyticsStationHourly),
        [_station_row(h, call, n // 24 + 1) for h in hours for call, n in stations.items()],
    )
    db_session.execute(
        insert(AnalyticsStationDaily),
        [_station_row(d, call, n) for d in days for call, n in stations.items()],
    )
    # A huge bucket exactly at the cut-off must never reach any baseline.
    db_session.execute(insert(AnalyticsBandHourly), [_band_row(AS_OF, "20m", 1_000_000)])
    db_session.flush()
    return db_session


def _stored(session: Session, **filters: str) -> int:
    query = select(func.count()).select_from(AnomalyBaseline)
    for column, value in filters.items():
        query = query.where(getattr(AnomalyBaseline, column) == value)
    return session.execute(query).scalar_one()


def test_refresh_stores_band_and_top_station_baselines(seeded: Session) -> None:
    result = refresh_baselines(seeded, as_of=AS_OF, config=CONFIG)
    seeded.flush()

    # 20m has hourly and daily rollups; 10m only hourly, so no daily baselines.
    band_rows = len(CONFIG.band_metrics) * (SLOTS + 24)
    station_rows = 2 * len(CONFIG.station_metrics) * SLOTS
    assert result.band_dimensions == 2
    assert result.station_dimensions == 2
    assert result.snapshot_count == band_rows + station_rows
    assert _stored(seeded, dimension_type="band") == band_rows
    assert _stored(seeded, dimension_type="station") == station_rows
    assert _stored(seeded, dimension_key="callsign=LOW3|direction=receiver") == 0
    assert load_coverage(seeded, baseline_version=CONFIG.version) == result.coverage

    busy_hour = seeded.execute(
        select(AnomalyBaseline).where(
            AnomalyBaseline.dimension_key == "band=20m|mode=FT8",
            AnomalyBaseline.metric == "observation_count",
            AnomalyBaseline.resolution == "hour",
            AnomalyBaseline.slot == 14,
        )
    ).scalar_one()
    assert busy_hour.quality == "sufficient"
    assert busy_hour.as_of == AS_OF
    assert busy_hour.cohort_end is not None and busy_hour.cohort_end < AS_OF
    assert 500 <= (busy_hour.expected_value or 0) <= 510

    quiet = seeded.execute(
        select(AnomalyBaseline.quality)
        .where(
            AnomalyBaseline.dimension_key == "band=10m|mode=FT8",
            AnomalyBaseline.metric == "observation_count",
            AnomalyBaseline.resolution == "hour",
        )
        .distinct()
    ).scalars()
    assert set(quiet) == {"sparse"}


def test_refresh_replaces_previous_set_and_prunes_old_versions(seeded: Session) -> None:
    first = refresh_baselines(seeded, as_of=AS_OF, config=CONFIG)
    seeded.execute(
        insert(AnomalyBaseline),
        [
            {
                "baseline_version": "superseded.0000000000",
                "dimension_type": "band",
                "dimension_key": "band=20m|mode=FT8",
                "metric": "observation_count",
                "resolution": "hour",
                "slot": 0,
                "as_of": AS_OF,
                "method": "seasonal_median_mad",
                "quality": "sufficient",
                "sample_count": 8,
                "transform": "log1p",
            }
        ],
    )

    narrower = replace(CONFIG, station_limit=1)
    assert narrower.version != CONFIG.version
    result = refresh_baselines(seeded, as_of=AS_OF, config=narrower)
    seeded.flush()

    # Every row of the previous version plus the superseded row is removed.
    assert result.pruned_rows == first.snapshot_count + 1
    assert _stored(seeded, baseline_version="superseded.0000000000") == 0
    assert _stored(seeded, baseline_version=CONFIG.version) == 0
    assert _stored(seeded, baseline_version=narrower.version) == result.snapshot_count
    assert _stored(seeded, dimension_type="station") == len(CONFIG.station_metrics) * SLOTS


def test_rerun_is_idempotent(seeded: Session) -> None:
    first = refresh_baselines(seeded, as_of=AS_OF, config=CONFIG)
    rows_before = seeded.execute(
        select(
            AnomalyBaseline.dimension_key, AnomalyBaseline.metric, AnomalyBaseline.center
        ).order_by(
            AnomalyBaseline.dimension_key,
            AnomalyBaseline.metric,
            AnomalyBaseline.resolution,
            AnomalyBaseline.slot,
        )
    ).all()

    second = refresh_baselines(seeded, as_of=AS_OF, config=CONFIG)
    rows_after = seeded.execute(
        select(
            AnomalyBaseline.dimension_key, AnomalyBaseline.metric, AnomalyBaseline.center
        ).order_by(
            AnomalyBaseline.dimension_key,
            AnomalyBaseline.metric,
            AnomalyBaseline.resolution,
            AnomalyBaseline.slot,
        )
    ).all()

    assert first.coverage == second.coverage
    assert second.pruned_rows == 0
    assert rows_before == rows_after
