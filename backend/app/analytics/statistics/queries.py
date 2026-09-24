from datetime import datetime
from typing import Literal

from sqlalchemy import Select, select

from app.infrastructure.database.base import Base
from app.infrastructure.database.models import (
    AnalyticsBandDaily,
    AnalyticsBandHourly,
    AnalyticsStationDaily,
    AnalyticsStationHourly,
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
