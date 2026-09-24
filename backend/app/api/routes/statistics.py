from datetime import datetime, timedelta
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.analytics.statistics.service import (
    BandRollup,
    BandStatistics,
    StationRollup,
    StatisticsService,
)
from app.api.dependencies import get_statistics_service
from app.api.validation import validate_time_range

router = APIRouter(
    prefix="/statistics",
    tags=["statistics"],
)


class SignalQualityResponse(BaseModel):
    snr_sample_count: int
    snr_coverage: float | None
    average_snr_db: float | None
    minimum_snr_db: int | None
    maximum_snr_db: int | None


class BandActivityResponse(BaseModel):
    observation_count: int
    active_station_count: int
    baseline_observation_count: float | None
    opening_strength: float | None


class BandStatisticsResponse(BaseModel):
    bucket_start: datetime
    bucket_end: datetime
    resolution: Literal["hour", "day"]
    band: str
    mode: str
    activity: BandActivityResponse
    signal_quality: SignalQualityResponse


class StationActivityResponse(BaseModel):
    sender_activity: int
    receiver_activity: int
    total_station_activity: int


class StationStatisticsResponse(BaseModel):
    start_time: datetime
    end_time: datetime
    resolution: Literal["hour", "day"]
    callsign: str
    activity: StationActivityResponse
    signal_quality: SignalQualityResponse


def get_bucket_end(
    bucket_start: datetime,
    resolution: Literal["hour", "day"],
) -> datetime:
    if resolution == "hour":
        return bucket_start + timedelta(hours=1)

    return bucket_start + timedelta(days=1)


def build_band_statistics_response(
    *,
    rollup: BandRollup,
    statistics: BandStatistics,
    bucket_end: datetime,
    resolution: Literal["hour", "day"],
) -> BandStatisticsResponse:
    return BandStatisticsResponse(
        bucket_start=rollup.bucket_start,
        bucket_end=bucket_end,
        resolution=resolution,
        band=rollup.band,
        mode=rollup.mode,
        activity=BandActivityResponse(
            observation_count=statistics.activity.observation_count,
            active_station_count=statistics.activity.active_station_count,
            baseline_observation_count=(statistics.activity.baseline_observation_count),
            opening_strength=statistics.activity.opening_strength,
        ),
        signal_quality=SignalQualityResponse(
            snr_sample_count=statistics.signal_quality.snr_sample_count,
            snr_coverage=statistics.signal_quality.snr_coverage,
            average_snr_db=statistics.signal_quality.average_snr_db,
            minimum_snr_db=statistics.signal_quality.minimum_snr_db,
            maximum_snr_db=statistics.signal_quality.maximum_snr_db,
        ),
    )


@router.get(
    "/bands",
    response_model=list[BandStatisticsResponse],
    summary="Get band statistics",
    description=(
        "Returns bucket-level amateur-radio band statistics for the requested "
        "time range. Results may be filtered by band and mode."
    ),
)
def get_band_statistics(
    service: Annotated[
        StatisticsService,
        Depends(get_statistics_service),
    ],
    start_time: Annotated[
        datetime,
        Query(
            description=("Start of the statistics range in UTC. The start timestamp is inclusive."),
            examples=["2026-09-23T00:00:00Z"],
        ),
    ],
    end_time: Annotated[
        datetime,
        Query(
            description=("End of the statistics range in UTC. The end timestamp is exclusive."),
            examples=["2026-09-24T00:00:00Z"],
        ),
    ],
    resolution: Annotated[
        Literal["hour", "day"],
        Query(
            description="Aggregation resolution.",
            examples=["hour"],
        ),
    ] = "hour",
    band: Annotated[
        str | None,
        Query(
            description="Filter statistics by amateur-radio band.",
            examples=["20m"],
        ),
    ] = None,
    mode: Annotated[
        str | None,
        Query(
            description="Filter statistics by operating mode.",
            examples=["FT8"],
        ),
    ] = None,
) -> list[BandStatisticsResponse]:
    validate_time_range(start_time, end_time)

    rollups = service.get_band_rollups(
        start_time=start_time,
        end_time=end_time,
        resolution=resolution,
        band=band,
        mode=mode,
    )

    responses: list[BandStatisticsResponse] = []

    for rollup in rollups:
        bucket_end = get_bucket_end(
            rollup.bucket_start,
            resolution,
        )

        statistics = service.get_band_statistics(
            bucket_start=rollup.bucket_start,
            bucket_end=bucket_end,
            resolution=resolution,
            band=rollup.band,
            mode=rollup.mode,
        )

        responses.append(
            build_band_statistics_response(
                rollup=rollup,
                statistics=statistics,
                bucket_end=bucket_end,
                resolution=resolution,
            )
        )

    return responses


@router.get(
    "/stations",
    response_model=list[StationStatisticsResponse],
    summary="Get station statistics",
    description=(
        "Returns amateur-radio station statistics for the requested time range. "
        "Results may be filtered by callsign."
    ),
)
def get_station_statistics(
    service: Annotated[
        StatisticsService,
        Depends(get_statistics_service),
    ],
    start_time: Annotated[
        datetime,
        Query(
            description=("Start of the statistics range in UTC. The start timestamp is inclusive."),
            examples=["2026-09-23T00:00:00Z"],
        ),
    ],
    end_time: Annotated[
        datetime,
        Query(
            description=("End of the statistics range in UTC. The end timestamp is exclusive."),
            examples=["2026-09-24T00:00:00Z"],
        ),
    ],
    resolution: Annotated[
        Literal["hour", "day"],
        Query(
            description="Aggregation resolution.",
            examples=["hour"],
        ),
    ] = "hour",
    callsign: Annotated[
        str | None,
        Query(
            description="Filter statistics by station callsign.",
            examples=["KK7QEA"],
        ),
    ] = None,
) -> list[StationStatisticsResponse]:
    validate_time_range(start_time, end_time)

    rollups = service.get_station_rollups(
        start_time=start_time,
        end_time=end_time,
        resolution=resolution,
        callsign=callsign,
    )

    rollups_by_callsign: dict[str, list[StationRollup]] = {}

    for rollup in rollups:
        rollups_by_callsign.setdefault(
            rollup.callsign,
            [],
        ).append(rollup)

    responses: list[StationStatisticsResponse] = []

    for station_callsign, station_rollups in rollups_by_callsign.items():
        statistics = service.calculate_station_statistics(
            rollups=station_rollups,
        )

        responses.append(
            StationStatisticsResponse(
                start_time=start_time,
                end_time=end_time,
                resolution=resolution,
                callsign=station_callsign,
                activity=StationActivityResponse(
                    sender_activity=statistics.activity.sender_activity,
                    receiver_activity=statistics.activity.receiver_activity,
                    total_station_activity=statistics.activity.total_station_activity,
                ),
                signal_quality=SignalQualityResponse(
                    snr_sample_count=statistics.signal_quality.snr_sample_count,
                    snr_coverage=statistics.signal_quality.snr_coverage,
                    average_snr_db=statistics.signal_quality.average_snr_db,
                    minimum_snr_db=statistics.signal_quality.minimum_snr_db,
                    maximum_snr_db=statistics.signal_quality.maximum_snr_db,
                ),
            )
        )

    return responses


class CorrelationResponse(BaseModel):
    correlation: float | None
    sample_count: int


class SolarCorrelationResponse(BaseModel):
    start_time: datetime
    end_time: datetime
    resolution: Literal["hour", "day"]
    observation_type: str
    band: str | None
    mode: str | None
    activity: CorrelationResponse
    signal_quality: CorrelationResponse


@router.get(
    "/solar-correlation",
    response_model=SolarCorrelationResponse,
    summary="Get solar-condition correlations",
    description=(
        "Returns correlations between a selected solar observation type "
        "and amateur-radio activity and signal quality."
    ),
)
def get_solar_correlation(
    service: Annotated[
        StatisticsService,
        Depends(get_statistics_service),
    ],
    start_time: Annotated[
        datetime,
        Query(
            description=("Start of the statistics range in UTC. The start timestamp is inclusive."),
            examples=["2026-09-23T00:00:00Z"],
        ),
    ],
    end_time: Annotated[
        datetime,
        Query(
            description=("End of the statistics range in UTC. The end timestamp is exclusive."),
            examples=["2026-09-24T00:00:00Z"],
        ),
    ],
    observation_type: Annotated[
        str,
        Query(
            description="Solar observation type to correlate.",
            examples=["kp_index"],
        ),
    ],
    resolution: Annotated[
        Literal["hour", "day"],
        Query(
            description="Aggregation resolution.",
            examples=["hour"],
        ),
    ] = "hour",
    band: Annotated[
        str | None,
        Query(
            description="Filter radio statistics by amateur-radio band.",
            examples=["20m"],
        ),
    ] = None,
    mode: Annotated[
        str | None,
        Query(
            description="Filter radio statistics by operating mode.",
            examples=["FT8"],
        ),
    ] = None,
) -> SolarCorrelationResponse:
    validate_time_range(start_time, end_time)

    statistics = service.get_solar_correlations(
        start_time=start_time,
        end_time=end_time,
        resolution=resolution,
        observation_type=observation_type,
        band=band,
        mode=mode,
    )

    return SolarCorrelationResponse(
        start_time=start_time,
        end_time=end_time,
        resolution=resolution,
        observation_type=observation_type,
        band=band,
        mode=mode,
        activity=CorrelationResponse(
            correlation=statistics.activity.correlation,
            sample_count=statistics.activity.sample_count,
        ),
        signal_quality=CorrelationResponse(
            correlation=statistics.signal_quality.correlation,
            sample_count=statistics.signal_quality.sample_count,
        ),
    )
