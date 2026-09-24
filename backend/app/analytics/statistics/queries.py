from datetime import datetime
from typing import Literal

from sqlalchemy import Select, func, select

from app.infrastructure.database.base import Base
from app.infrastructure.database.models import (
    AnalyticsBandDaily,
    AnalyticsBandHourly,
    AnalyticsStationDaily,
    AnalyticsStationHourly,
    SolarCondition,
)

BucketResolution = Literal["hour", "day"]
StationDirection = Literal["sender", "receiver"]


def build_band_statistics_query(
    *,
    start_time: datetime,
    end_time: datetime,
    resolution: BucketResolution,
    band: str | None = None,
    mode: str | None = None,
) -> Select[tuple[Base]]:
    model = AnalyticsBandHourly if resolution == "hour" else AnalyticsBandDaily

    query = select(model).where(
        model.bucket_start >= start_time,
        model.bucket_start < end_time,
    )

    if band is not None:
        query = query.where(model.band == band)

    if mode is not None:
        query = query.where(model.mode == mode)

    return query.order_by(
        model.bucket_start,
        model.band,
        model.mode,
    )


def build_station_statistics_query(
    *,
    start_time: datetime,
    end_time: datetime,
    resolution: BucketResolution,
    callsign: str | None = None,
    direction: StationDirection | None = None,
) -> Select[tuple[Base]]:
    model = AnalyticsStationHourly if resolution == "hour" else AnalyticsStationDaily

    query = select(model).where(
        model.bucket_start >= start_time,
        model.bucket_start < end_time,
    )

    if callsign is not None:
        query = query.where(model.callsign == callsign)

    if direction is not None:
        query = query.where(model.direction == direction)

    return query.order_by(
        model.bucket_start,
        model.callsign,
        model.direction,
    )


def build_solar_statistics_query(
    *,
    start_time: datetime,
    end_time: datetime,
    resolution: BucketResolution,
    observation_type: str,
) -> Select[tuple[datetime, float]]:
    bucket_start = func.date_trunc(
        resolution,
        SolarCondition.observed_at,
    ).label("bucket_start")

    average_value = func.avg(
        SolarCondition.value,
    ).label("average_value")

    return (
        select(
            bucket_start,
            average_value,
        )
        .where(
            SolarCondition.observed_at >= start_time,
            SolarCondition.observed_at < end_time,
            SolarCondition.observation_type == observation_type,
            SolarCondition.value.is_not(None),
        )
        .group_by(bucket_start)
        .order_by(bucket_start)
    )
