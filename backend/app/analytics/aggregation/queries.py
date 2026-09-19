from datetime import datetime
from typing import Literal

from sqlalchemy import Select, func, select

from app.infrastructure.database.models import Spot

StationDirection = Literal["sender", "receiver"]


def _build_band_aggregation_query(
    *,
    start_time: datetime,
    end_time: datetime,
    bucket_resolution: str,
) -> Select[tuple[object, ...]]:
    bucket_start = func.date_trunc(
        bucket_resolution,
        Spot.observed_at,
    ).label("bucket_start")

    return (
        select(
            bucket_start,
            Spot.band,
            Spot.mode,
            func.count(Spot.id).label("observation_count"),
            func.count(func.distinct(Spot.sender_callsign)).label("unique_sender_count"),
            func.count(func.distinct(Spot.receiver_callsign)).label("unique_receiver_count"),
            func.count(Spot.snr_db).label("snr_sample_count"),
            func.min(Spot.snr_db).label("snr_min_db"),
            func.max(Spot.snr_db).label("snr_max_db"),
            func.avg(Spot.snr_db).label("snr_avg_db"),
        )
        .where(
            Spot.observed_at >= start_time,
            Spot.observed_at < end_time,
            Spot.band.is_not(None),
        )
        .group_by(
            bucket_start,
            Spot.band,
            Spot.mode,
        )
        .order_by(
            bucket_start,
            Spot.band,
            Spot.mode,
        )
    )


def _build_station_aggregation_query(
    *,
    start_time: datetime,
    end_time: datetime,
    bucket_resolution: str,
    direction: StationDirection,
) -> Select[tuple[object, ...]]:
    bucket_start = func.date_trunc(
        bucket_resolution,
        Spot.observed_at,
    ).label("bucket_start")

    if direction == "sender":
        station_id = Spot.sender_station_id
        callsign = Spot.sender_callsign
        counterparty = Spot.receiver_callsign
    else:
        station_id = Spot.receiver_station_id
        callsign = Spot.receiver_callsign
        counterparty = Spot.sender_callsign

    return (
        select(
            bucket_start,
            func.max(station_id).label("station_id"),
            callsign.label("callsign"),
            func.count(Spot.id).label("observation_count"),
            func.count(func.distinct(counterparty)).label("unique_counterparty_count"),
            func.count(Spot.snr_db).label("snr_sample_count"),
            func.min(Spot.snr_db).label("snr_min_db"),
            func.max(Spot.snr_db).label("snr_max_db"),
            func.avg(Spot.snr_db).label("snr_avg_db"),
        )
        .where(
            Spot.observed_at >= start_time,
            Spot.observed_at < end_time,
        )
        .group_by(
            bucket_start,
            callsign,
        )
        .order_by(
            bucket_start,
            callsign,
        )
    )


def build_hourly_band_aggregation_query(
    *,
    start_time: datetime,
    end_time: datetime,
) -> Select[tuple[object, ...]]:
    return _build_band_aggregation_query(
        start_time=start_time,
        end_time=end_time,
        bucket_resolution="hour",
    )


def build_daily_band_aggregation_query(
    *,
    start_time: datetime,
    end_time: datetime,
) -> Select[tuple[object, ...]]:
    return _build_band_aggregation_query(
        start_time=start_time,
        end_time=end_time,
        bucket_resolution="day",
    )


def build_hourly_station_aggregation_query(
    *,
    start_time: datetime,
    end_time: datetime,
    direction: StationDirection,
) -> Select[tuple[object, ...]]:
    return _build_station_aggregation_query(
        start_time=start_time,
        end_time=end_time,
        bucket_resolution="hour",
        direction=direction,
    )


def build_daily_station_aggregation_query(
    *,
    start_time: datetime,
    end_time: datetime,
    direction: StationDirection,
) -> Select[tuple[object, ...]]:
    return _build_station_aggregation_query(
        start_time=start_time,
        end_time=end_time,
        bucket_resolution="day",
        direction=direction,
    )
