from collections.abc import Iterator, Mapping, Sequence
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

# PostgreSQL's wire protocol allows at most 65,535 bind parameters per
# statement. A multi-row INSERT uses one parameter per column per row, so busy
# hours (thousands of active stations) must be written in several statements.
MAX_BIND_PARAMETERS = 65_535


def _chunked(
    values: list[dict[str, Any]],
) -> Iterator[list[dict[str, Any]]]:
    columns = max(len(values[0]), 1)
    rows_per_statement = max(MAX_BIND_PARAMETERS // columns, 1)
    for start in range(0, len(values), rows_per_statement):
        yield values[start : start + rows_per_statement]


def upsert_band_rollups(
    session: Session,
    *,
    model: BandRollupModel,
    rows: AggregationRows,
) -> None:
    if not rows:
        return

    for chunk in _chunked([dict(row) for row in rows]):
        _upsert_band_chunk(session, model=model, values=chunk)


def _upsert_band_chunk(
    session: Session,
    *,
    model: BandRollupModel,
    values: list[dict[str, Any]],
) -> None:
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

    for chunk in _chunked(values):
        _upsert_station_chunk(session, model=model, values=chunk)


def _upsert_station_chunk(
    session: Session,
    *,
    model: StationRollupModel,
    values: list[dict[str, Any]],
) -> None:
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
