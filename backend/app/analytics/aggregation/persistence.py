from collections.abc import Mapping, Sequence
from typing import Any

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.infrastructure.database.models import (
    AnalyticsBandDaily,
    AnalyticsBandHourly,
    AnalyticsStationDaily,
    AnalyticsStationHourly,
)

BandRollupModel = type[AnalyticsBandHourly] | type[AnalyticsBandDaily]
StationRollupModel = type[AnalyticsStationHourly] | type[AnalyticsStationDaily]

AggregationRow = Mapping[str, Any]
AggregationRows = Sequence[AggregationRow]


def upsert_band_rollups(
    session: Session,
    *,
    model: BandRollupModel,
    rows: AggregationRows,
) -> None:
    if not rows:
        return

    values = [dict(row) for row in rows]

    statement = insert(model).values(values)

    statement = statement.on_conflict_do_update(
        index_elements=[
            model.bucket_start,
            model.band,
            model.mode,
        ],
        set_={
            "observation_count": statement.excluded.observation_count,
            "unique_sender_count": statement.excluded.unique_sender_count,
            "unique_receiver_count": statement.excluded.unique_receiver_count,
            "snr_sample_count": statement.excluded.snr_sample_count,
            "snr_min_db": statement.excluded.snr_min_db,
            "snr_max_db": statement.excluded.snr_max_db,
            "snr_avg_db": statement.excluded.snr_avg_db,
        },
    )

    session.execute(statement)


def upsert_station_rollups(
    session: Session,
    *,
    model: StationRollupModel,
    rows: AggregationRows,
    direction: str,
) -> None:
    if not rows:
        return

    values = [
        {
            **dict(row),
            "direction": direction,
        }
        for row in rows
    ]

    statement = insert(model).values(values)

    statement = statement.on_conflict_do_update(
        index_elements=[
            model.bucket_start,
            model.callsign,
            model.direction,
        ],
        set_={
            "station_id": statement.excluded.station_id,
            "observation_count": statement.excluded.observation_count,
            "unique_counterparty_count": statement.excluded.unique_counterparty_count,
            "snr_sample_count": statement.excluded.snr_sample_count,
            "snr_min_db": statement.excluded.snr_min_db,
            "snr_max_db": statement.excluded.snr_max_db,
            "snr_avg_db": statement.excluded.snr_avg_db,
        },
    )

    session.execute(statement)
