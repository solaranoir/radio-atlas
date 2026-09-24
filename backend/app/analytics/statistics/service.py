from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.analytics.statistics.cache import StatisticsCache
from app.analytics.statistics.metrics import (
    BandActivityMetrics,
    SignalQualityMetrics,
    SignalQualityRollup,
    StationActivityMetrics,
    calculate_activity_baseline,
    calculate_band_activity,
    calculate_station_activity,
    combine_signal_quality,
)
from app.analytics.statistics.queries import (
    BucketResolution,
    StationDirection,
    build_band_statistics_query,
    build_station_statistics_query,
)
from app.infrastructure.database.models import (
    AnalyticsBandDaily,
    AnalyticsBandHourly,
    AnalyticsStationDaily,
    AnalyticsStationHourly,
)


@dataclass(frozen=True)
class BandRollup:
    bucket_start: datetime
    band: str
    mode: str
    observation_count: int
    unique_sender_count: int
    unique_receiver_count: int
    snr_sample_count: int
    snr_min_db: int | None
    snr_max_db: int | None
    snr_avg_db: float | None


@dataclass(frozen=True)
class BandStatistics:
    activity: BandActivityMetrics
    signal_quality: SignalQualityMetrics


@dataclass(frozen=True)
class StationStatistics:
    activity: StationActivityMetrics
    signal_quality: SignalQualityMetrics


@dataclass(frozen=True)
class StationRollup:
    bucket_start: datetime
    station_id: int | None
    callsign: str
    direction: str
    observation_count: int
    unique_counterparty_count: int
    snr_sample_count: int
    snr_min_db: int | None
    snr_max_db: int | None
    snr_avg_db: float | None


def get_baseline_window(
    *,
    bucket_start: datetime,
    resolution: BucketResolution,
) -> tuple[datetime, datetime, int]:
    if resolution == "hour":
        bucket_count = 24
        start_time = bucket_start - timedelta(hours=bucket_count)
    else:
        bucket_count = 7
        start_time = bucket_start - timedelta(days=bucket_count)

    return start_time, bucket_start, bucket_count


def build_band_statistics_cache_key(
    *,
    bucket_start: datetime,
    bucket_end: datetime,
    resolution: BucketResolution,
    band: str,
    mode: str,
) -> str:
    return (
        "statistics:band:"
        f"{resolution}:"
        f"{band}:"
        f"{mode}:"
        f"{bucket_start.isoformat()}:"
        f"{bucket_end.isoformat()}"
    )


def serialize_band_statistics(
    statistics: BandStatistics,
) -> dict[str, object]:
    return {
        "activity": {
            "observation_count": statistics.activity.observation_count,
            "active_station_count": statistics.activity.active_station_count,
            "baseline_observation_count": (statistics.activity.baseline_observation_count),
            "opening_strength": statistics.activity.opening_strength,
        },
        "signal_quality": {
            "snr_sample_count": statistics.signal_quality.snr_sample_count,
            "snr_coverage": statistics.signal_quality.snr_coverage,
            "average_snr_db": statistics.signal_quality.average_snr_db,
            "minimum_snr_db": statistics.signal_quality.minimum_snr_db,
            "maximum_snr_db": statistics.signal_quality.maximum_snr_db,
        },
    }


def deserialize_band_statistics(
    value: dict[str, object],
) -> BandStatistics | None:
    activity = value.get("activity")
    signal_quality = value.get("signal_quality")

    if not isinstance(activity, dict) or not isinstance(
        signal_quality,
        dict,
    ):
        return None

    try:
        return BandStatistics(
            activity=BandActivityMetrics(
                observation_count=int(activity["observation_count"]),
                active_station_count=int(activity["active_station_count"]),
                baseline_observation_count=(
                    float(activity["baseline_observation_count"])
                    if activity["baseline_observation_count"] is not None
                    else None
                ),
                opening_strength=(
                    float(activity["opening_strength"])
                    if activity["opening_strength"] is not None
                    else None
                ),
            ),
            signal_quality=SignalQualityMetrics(
                snr_sample_count=int(signal_quality["snr_sample_count"]),
                snr_coverage=(
                    float(signal_quality["snr_coverage"])
                    if signal_quality["snr_coverage"] is not None
                    else None
                ),
                average_snr_db=(
                    float(signal_quality["average_snr_db"])
                    if signal_quality["average_snr_db"] is not None
                    else None
                ),
                minimum_snr_db=(
                    int(signal_quality["minimum_snr_db"])
                    if signal_quality["minimum_snr_db"] is not None
                    else None
                ),
                maximum_snr_db=(
                    int(signal_quality["maximum_snr_db"])
                    if signal_quality["maximum_snr_db"] is not None
                    else None
                ),
            ),
        )
    except (KeyError, TypeError, ValueError):
        return None


class StatisticsService:
    def __init__(
        self,
        session: Session,
        cache: StatisticsCache | None = None,
    ) -> None:
        self._session = session
        self._cache = cache

    def get_band_rollups(
        self,
        *,
        start_time: datetime,
        end_time: datetime,
        resolution: BucketResolution,
        band: str | None = None,
        mode: str | None = None,
    ) -> list[BandRollup]:
        query = build_band_statistics_query(
            start_time=start_time,
            end_time=end_time,
            resolution=resolution,
            band=band,
            mode=mode,
        )

        results: list[BandRollup] = []

        for row in self._session.scalars(query):
            if not isinstance(
                row,
                (AnalyticsBandHourly, AnalyticsBandDaily),
            ):
                continue

            results.append(
                BandRollup(
                    bucket_start=row.bucket_start,
                    band=row.band,
                    mode=row.mode,
                    observation_count=row.observation_count,
                    unique_sender_count=row.unique_sender_count,
                    unique_receiver_count=row.unique_receiver_count,
                    snr_sample_count=row.snr_sample_count,
                    snr_min_db=row.snr_min_db,
                    snr_max_db=row.snr_max_db,
                    snr_avg_db=row.snr_avg_db,
                )
            )

        return results

    def get_band_baseline_counts(
        self,
        *,
        bucket_start: datetime,
        resolution: BucketResolution,
        band: str,
        mode: str,
    ) -> tuple[list[int], int]:
        start_time, end_time, bucket_count = get_baseline_window(
            bucket_start=bucket_start,
            resolution=resolution,
        )

        rollups = self.get_band_rollups(
            start_time=start_time,
            end_time=end_time,
            resolution=resolution,
            band=band,
            mode=mode,
        )

        return (
            [rollup.observation_count for rollup in rollups],
            bucket_count,
        )

    def calculate_band_statistics(
        self,
        *,
        rollups: list[BandRollup],
        baseline_counts: list[int],
        expected_baseline_bucket_count: int,
    ) -> BandStatistics:

        if len(rollups) > 1:
            raise ValueError("Band activity statistics require a single rollup bucket")

        observation_count = sum(rollup.observation_count for rollup in rollups)
        unique_sender_count = sum(rollup.unique_sender_count for rollup in rollups)
        unique_receiver_count = sum(rollup.unique_receiver_count for rollup in rollups)

        baseline = calculate_activity_baseline(
            observation_counts=baseline_counts,
            expected_bucket_count=expected_baseline_bucket_count,
        )

        activity = calculate_band_activity(
            observation_count=observation_count,
            unique_sender_count=unique_sender_count,
            unique_receiver_count=unique_receiver_count,
            baseline_observation_count=baseline,
        )

        signal_quality = combine_signal_quality(
            [
                SignalQualityRollup(
                    observation_count=rollup.observation_count,
                    snr_sample_count=rollup.snr_sample_count,
                    snr_avg_db=rollup.snr_avg_db,
                    snr_min_db=rollup.snr_min_db,
                    snr_max_db=rollup.snr_max_db,
                )
                for rollup in rollups
            ]
        )

        return BandStatistics(
            activity=activity,
            signal_quality=signal_quality,
        )

    def get_station_rollups(
        self,
        *,
        start_time: datetime,
        end_time: datetime,
        resolution: BucketResolution,
        callsign: str | None = None,
        direction: StationDirection | None = None,
    ) -> list[StationRollup]:
        query = build_station_statistics_query(
            start_time=start_time,
            end_time=end_time,
            resolution=resolution,
            callsign=callsign,
            direction=direction,
        )

        results: list[StationRollup] = []

        for row in self._session.scalars(query):
            if not isinstance(
                row,
                (AnalyticsStationHourly, AnalyticsStationDaily),
            ):
                continue

            results.append(
                StationRollup(
                    bucket_start=row.bucket_start,
                    station_id=row.station_id,
                    callsign=row.callsign,
                    direction=row.direction,
                    observation_count=row.observation_count,
                    unique_counterparty_count=row.unique_counterparty_count,
                    snr_sample_count=row.snr_sample_count,
                    snr_min_db=row.snr_min_db,
                    snr_max_db=row.snr_max_db,
                    snr_avg_db=row.snr_avg_db,
                )
            )

        return results

    def calculate_station_statistics(
        self,
        *,
        rollups: list[StationRollup],
    ) -> StationStatistics:
        sender_activity = sum(
            rollup.observation_count for rollup in rollups if rollup.direction == "sender"
        )
        receiver_activity = sum(
            rollup.observation_count for rollup in rollups if rollup.direction == "receiver"
        )

        activity = calculate_station_activity(
            sender_activity=sender_activity,
            receiver_activity=receiver_activity,
        )

        signal_quality = combine_signal_quality(
            [
                SignalQualityRollup(
                    observation_count=rollup.observation_count,
                    snr_sample_count=rollup.snr_sample_count,
                    snr_avg_db=rollup.snr_avg_db,
                    snr_min_db=rollup.snr_min_db,
                    snr_max_db=rollup.snr_max_db,
                )
                for rollup in rollups
            ]
        )

        return StationStatistics(
            activity=activity,
            signal_quality=signal_quality,
        )

    def get_band_statistics(
        self,
        *,
        bucket_start: datetime,
        bucket_end: datetime,
        resolution: BucketResolution,
        band: str,
        mode: str,
    ) -> BandStatistics:

        cache_key = build_band_statistics_cache_key(
            bucket_start=bucket_start,
            bucket_end=bucket_end,
            resolution=resolution,
            band=band,
            mode=mode,
        )

        if self._cache is not None:
            cached_value = self._cache.get(cache_key)

            if cached_value is not None:
                cached_statistics = deserialize_band_statistics(cached_value)

                if cached_statistics is not None:
                    return cached_statistics

        rollups = self.get_band_rollups(
            start_time=bucket_start,
            end_time=bucket_end,
            resolution=resolution,
            band=band,
            mode=mode,
        )

        baseline_counts, expected_bucket_count = self.get_band_baseline_counts(
            bucket_start=bucket_start,
            resolution=resolution,
            band=band,
            mode=mode,
        )

        statistics = self.calculate_band_statistics(
            rollups=rollups,
            baseline_counts=baseline_counts,
            expected_baseline_bucket_count=expected_bucket_count,
        )

        if self._cache is not None:
            self._cache.set(
                cache_key,
                serialize_band_statistics(statistics),
            )

        return statistics
