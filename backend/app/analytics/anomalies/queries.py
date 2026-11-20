"""Rollup reads for baseline modeling. Read-only; never touches raw spots."""

from collections import defaultdict
from collections.abc import Sequence
from datetime import datetime
from typing import Any

from sqlalchemy import func, select, tuple_
from sqlalchemy.orm import Session

from app.analytics.anomalies.models import DimensionKey, Resolution
from app.infrastructure.database.models import (
    AnalyticsBandDaily,
    AnalyticsBandHourly,
    AnalyticsStationDaily,
    AnalyticsStationHourly,
)

RollupRows = dict[DimensionKey, list[dict[str, Any]]]

_BAND_COLUMNS = (
    "bucket_start",
    "band",
    "mode",
    "observation_count",
    "unique_sender_count",
    "unique_receiver_count",
    "snr_sample_count",
    "snr_avg_db",
)
_STATION_COLUMNS = (
    "bucket_start",
    "callsign",
    "direction",
    "observation_count",
    "unique_counterparty_count",
    "snr_sample_count",
    "snr_avg_db",
)


def _band_model(resolution: Resolution) -> type[AnalyticsBandHourly] | type[AnalyticsBandDaily]:
    return AnalyticsBandHourly if resolution == "hour" else AnalyticsBandDaily


def _station_model(
    resolution: Resolution,
) -> type[AnalyticsStationHourly] | type[AnalyticsStationDaily]:
    return AnalyticsStationHourly if resolution == "hour" else AnalyticsStationDaily


def load_active_buckets(
    session: Session,
    *,
    resolution: Resolution,
    start: datetime,
    end: datetime,
) -> list[datetime]:
    """Buckets in [start, end) in which ingestion produced any band rollup.

    Used to tell true zero activity (ingestion running, nothing heard) from
    ingestion gaps (no data anywhere), which must never be zero-filled.
    """

    model = _band_model(resolution)
    rows = session.execute(
        select(model.bucket_start)
        .where(model.bucket_start >= start, model.bucket_start < end)
        .distinct()
        .order_by(model.bucket_start)
    )
    return list(rows.scalars())


def load_band_rollups(
    session: Session,
    *,
    resolution: Resolution,
    start: datetime,
    end: datetime,
) -> RollupRows:
    model = _band_model(resolution)
    columns = [getattr(model, name) for name in _BAND_COLUMNS]
    rows = session.execute(
        select(*columns)
        .where(model.bucket_start >= start, model.bucket_start < end)
        .order_by(model.band, model.mode, model.bucket_start)
    )
    grouped: RollupRows = defaultdict(list)
    for row in rows.mappings():
        grouped[DimensionKey.band(row["band"], row["mode"])].append(dict(row))
    return dict(grouped)


def select_top_stations(
    session: Session,
    *,
    start: datetime,
    end: datetime,
    limit: int,
) -> list[DimensionKey]:
    """The ``limit`` busiest callsign/direction pairs by daily rollup volume.

    Ties break on callsign then direction so the selection is deterministic.
    """

    if limit <= 0:
        return []
    total = func.sum(AnalyticsStationDaily.observation_count)
    rows = session.execute(
        select(AnalyticsStationDaily.callsign, AnalyticsStationDaily.direction)
        .where(
            AnalyticsStationDaily.bucket_start >= start,
            AnalyticsStationDaily.bucket_start < end,
        )
        .group_by(AnalyticsStationDaily.callsign, AnalyticsStationDaily.direction)
        .order_by(
            total.desc(),
            AnalyticsStationDaily.callsign,
            AnalyticsStationDaily.direction,
        )
        .limit(limit)
    )
    return [DimensionKey.station(callsign, direction) for callsign, direction in rows]


def load_station_rollups(
    session: Session,
    *,
    resolution: Resolution,
    start: datetime,
    end: datetime,
    stations: Sequence[DimensionKey],
) -> RollupRows:
    if not stations:
        return {}
    model = _station_model(resolution)
    columns = [getattr(model, name) for name in _STATION_COLUMNS]
    pairs = [(key.primary, key.secondary) for key in stations]
    rows = session.execute(
        select(*columns)
        .where(
            model.bucket_start >= start,
            model.bucket_start < end,
            tuple_(model.callsign, model.direction).in_(pairs),
        )
        .order_by(model.callsign, model.direction, model.bucket_start)
    )
    grouped: RollupRows = {key: [] for key in stations}
    for row in rows.mappings():
        grouped[DimensionKey.station(row["callsign"], row["direction"])].append(dict(row))
    return grouped
