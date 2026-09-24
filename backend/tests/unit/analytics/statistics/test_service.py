from datetime import UTC, datetime
from unittest.mock import Mock, patch

import pytest
from sqlalchemy.orm import Session

from app.analytics.statistics.cache import StatisticsCache
from app.analytics.statistics.service import (
    BandRollup,
    SolarRollup,
    StationRollup,
    StatisticsService,
    get_baseline_window,
)


def test_calculate_band_statistics() -> None:
    service = StatisticsService(Mock(spec=Session))

    rollup = BandRollup(
        bucket_start=datetime(2026, 9, 23, 12, tzinfo=UTC),
        band="20m",
        mode="FT8",
        observation_count=120,
        unique_sender_count=30,
        unique_receiver_count=40,
        snr_sample_count=60,
        snr_min_db=-24,
        snr_max_db=8,
        snr_avg_db=-7.5,
    )

    result = service.calculate_band_statistics(
        rollups=[rollup],
        baseline_counts=[40, 60, 80],
        expected_baseline_bucket_count=3,
    )

    assert result.activity.observation_count == 120
    assert result.activity.active_station_count == 70
    assert result.activity.baseline_observation_count == pytest.approx(60.0)
    assert result.activity.opening_strength == pytest.approx(2.0)

    assert result.signal_quality.snr_sample_count == 60
    assert result.signal_quality.snr_coverage == pytest.approx(0.5)
    assert result.signal_quality.average_snr_db == pytest.approx(-7.5)
    assert result.signal_quality.minimum_snr_db == -24
    assert result.signal_quality.maximum_snr_db == 8


def test_calculate_band_statistics_rejects_multiple_buckets() -> None:
    service = StatisticsService(Mock(spec=Session))

    rollup = BandRollup(
        bucket_start=datetime(2026, 9, 23, 12, tzinfo=UTC),
        band="20m",
        mode="FT8",
        observation_count=10,
        unique_sender_count=4,
        unique_receiver_count=5,
        snr_sample_count=2,
        snr_min_db=-15,
        snr_max_db=-5,
        snr_avg_db=-10.0,
    )

    with pytest.raises(
        ValueError,
        match="Band activity statistics require a single rollup bucket",
    ):
        service.calculate_band_statistics(
            rollups=[rollup, rollup],
            baseline_counts=[10, 20],
            expected_baseline_bucket_count=2,
        )


def test_calculate_station_statistics_across_multiple_buckets() -> None:
    service = StatisticsService(Mock(spec=Session))

    rollups = [
        StationRollup(
            bucket_start=datetime(2026, 9, 23, 12, tzinfo=UTC),
            station_id=1,
            callsign="KK7QEA",
            direction="sender",
            observation_count=10,
            unique_counterparty_count=6,
            snr_sample_count=5,
            snr_min_db=-18,
            snr_max_db=-4,
            snr_avg_db=-10.0,
        ),
        StationRollup(
            bucket_start=datetime(2026, 9, 23, 13, tzinfo=UTC),
            station_id=1,
            callsign="KK7QEA",
            direction="receiver",
            observation_count=20,
            unique_counterparty_count=12,
            snr_sample_count=5,
            snr_min_db=-12,
            snr_max_db=6,
            snr_avg_db=0.0,
        ),
    ]

    result = service.calculate_station_statistics(rollups=rollups)

    assert result.activity.sender_activity == 10
    assert result.activity.receiver_activity == 20
    assert result.activity.total_station_activity == 30

    assert result.signal_quality.snr_sample_count == 10
    assert result.signal_quality.snr_coverage == pytest.approx(10 / 30)
    assert result.signal_quality.average_snr_db == pytest.approx(-5.0)
    assert result.signal_quality.minimum_snr_db == -18
    assert result.signal_quality.maximum_snr_db == 6


def test_get_hourly_baseline_window() -> None:
    bucket_start = datetime(2026, 9, 23, 12, tzinfo=UTC)

    start_time, end_time, bucket_count = get_baseline_window(
        bucket_start=bucket_start,
        resolution="hour",
    )

    assert start_time == datetime(2026, 9, 22, 12, tzinfo=UTC)
    assert end_time == bucket_start
    assert bucket_count == 24


def test_get_daily_baseline_window() -> None:
    bucket_start = datetime(2026, 9, 23, tzinfo=UTC)

    start_time, end_time, bucket_count = get_baseline_window(
        bucket_start=bucket_start,
        resolution="day",
    )

    assert start_time == datetime(2026, 9, 16, tzinfo=UTC)
    assert end_time == bucket_start
    assert bucket_count == 7


def test_get_band_baseline_counts() -> None:
    service = StatisticsService(Mock(spec=Session))
    bucket_start = datetime(2026, 9, 23, 12, tzinfo=UTC)

    rollups = [
        BandRollup(
            bucket_start=datetime(2026, 9, 23, 9, tzinfo=UTC),
            band="20m",
            mode="FT8",
            observation_count=40,
            unique_sender_count=10,
            unique_receiver_count=12,
            snr_sample_count=20,
            snr_min_db=-20,
            snr_max_db=5,
            snr_avg_db=-8.0,
        ),
        BandRollup(
            bucket_start=datetime(2026, 9, 23, 10, tzinfo=UTC),
            band="20m",
            mode="FT8",
            observation_count=60,
            unique_sender_count=14,
            unique_receiver_count=16,
            snr_sample_count=30,
            snr_min_db=-18,
            snr_max_db=7,
            snr_avg_db=-6.0,
        ),
    ]

    with patch.object(
        service,
        "get_band_rollups",
        return_value=rollups,
    ) as get_band_rollups:
        counts, expected_bucket_count = service.get_band_baseline_counts(
            bucket_start=bucket_start,
            resolution="hour",
            band="20m",
            mode="FT8",
        )

    assert counts == [40, 60]
    assert expected_bucket_count == 24

    get_band_rollups.assert_called_once_with(
        start_time=datetime(2026, 9, 22, 12, tzinfo=UTC),
        end_time=bucket_start,
        resolution="hour",
        band="20m",
        mode="FT8",
    )


def test_get_band_statistics_uses_rollup_and_baseline_data() -> None:
    service = StatisticsService(Mock(spec=Session))
    bucket_start = datetime(2026, 9, 23, 12, tzinfo=UTC)
    bucket_end = datetime(2026, 9, 23, 13, tzinfo=UTC)

    rollup = BandRollup(
        bucket_start=bucket_start,
        band="20m",
        mode="FT8",
        observation_count=120,
        unique_sender_count=30,
        unique_receiver_count=40,
        snr_sample_count=60,
        snr_min_db=-24,
        snr_max_db=8,
        snr_avg_db=-7.5,
    )

    with (
        patch.object(
            service,
            "get_band_rollups",
            return_value=[rollup],
        ) as get_band_rollups,
        patch.object(
            service,
            "get_band_baseline_counts",
            return_value=([40, 60, 80], 3),
        ) as get_band_baseline_counts,
    ):
        result = service.get_band_statistics(
            bucket_start=bucket_start,
            bucket_end=bucket_end,
            resolution="hour",
            band="20m",
            mode="FT8",
        )

    assert result.activity.observation_count == 120
    assert result.activity.baseline_observation_count == pytest.approx(60.0)
    assert result.activity.opening_strength == pytest.approx(2.0)
    assert result.signal_quality.average_snr_db == pytest.approx(-7.5)

    get_band_rollups.assert_called_once_with(
        start_time=bucket_start,
        end_time=bucket_end,
        resolution="hour",
        band="20m",
        mode="FT8",
    )

    get_band_baseline_counts.assert_called_once_with(
        bucket_start=bucket_start,
        resolution="hour",
        band="20m",
        mode="FT8",
    )


def test_get_band_statistics_returns_cached_result() -> None:
    cache = Mock(spec=StatisticsCache)
    cache.get.return_value = {
        "activity": {
            "observation_count": 120,
            "active_station_count": 70,
            "baseline_observation_count": 60.0,
            "opening_strength": 2.0,
        },
        "signal_quality": {
            "snr_sample_count": 60,
            "snr_coverage": 0.5,
            "average_snr_db": -7.5,
            "minimum_snr_db": -24,
            "maximum_snr_db": 8,
        },
    }

    service = StatisticsService(
        Mock(spec=Session),
        cache=cache,
    )

    bucket_start = datetime(2026, 9, 23, 12, tzinfo=UTC)
    bucket_end = datetime(2026, 9, 23, 13, tzinfo=UTC)

    result = service.get_band_statistics(
        bucket_start=bucket_start,
        bucket_end=bucket_end,
        resolution="hour",
        band="20m",
        mode="FT8",
    )

    assert result.activity.observation_count == 120
    assert result.activity.opening_strength == pytest.approx(2.0)
    assert result.signal_quality.average_snr_db == pytest.approx(-7.5)

    cache.get.assert_called_once()
    cache.set.assert_not_called()


def test_get_band_statistics_caches_computed_result() -> None:
    cache = Mock(spec=StatisticsCache)
    cache.get.return_value = None

    service = StatisticsService(
        Mock(spec=Session),
        cache=cache,
    )

    bucket_start = datetime(2026, 9, 23, 12, tzinfo=UTC)
    bucket_end = datetime(2026, 9, 23, 13, tzinfo=UTC)

    rollup = BandRollup(
        bucket_start=bucket_start,
        band="20m",
        mode="FT8",
        observation_count=120,
        unique_sender_count=30,
        unique_receiver_count=40,
        snr_sample_count=60,
        snr_min_db=-24,
        snr_max_db=8,
        snr_avg_db=-7.5,
    )

    with (
        patch.object(
            service,
            "get_band_rollups",
            return_value=[rollup],
        ),
        patch.object(
            service,
            "get_band_baseline_counts",
            return_value=([40, 60, 80], 3),
        ),
    ):
        result = service.get_band_statistics(
            bucket_start=bucket_start,
            bucket_end=bucket_end,
            resolution="hour",
            band="20m",
            mode="FT8",
        )

    assert result.activity.opening_strength == pytest.approx(2.0)

    cache.get.assert_called_once()
    cache.set.assert_called_once()

    cached_value = cache.set.call_args.args[1]

    assert cached_value["activity"]["observation_count"] == 120
    assert cached_value["activity"]["opening_strength"] == pytest.approx(2.0)
    assert cached_value["signal_quality"]["average_snr_db"] == pytest.approx(-7.5)


def test_get_band_statistics_recomputes_malformed_cached_result() -> None:
    cache = Mock(spec=StatisticsCache)
    cache.get.return_value = {"unexpected": "data"}

    service = StatisticsService(
        Mock(spec=Session),
        cache=cache,
    )

    bucket_start = datetime(2026, 9, 23, 12, tzinfo=UTC)
    bucket_end = datetime(2026, 9, 23, 13, tzinfo=UTC)

    rollup = BandRollup(
        bucket_start=bucket_start,
        band="20m",
        mode="FT8",
        observation_count=120,
        unique_sender_count=30,
        unique_receiver_count=40,
        snr_sample_count=60,
        snr_min_db=-24,
        snr_max_db=8,
        snr_avg_db=-7.5,
    )

    with (
        patch.object(
            service,
            "get_band_rollups",
            return_value=[rollup],
        ),
        patch.object(
            service,
            "get_band_baseline_counts",
            return_value=([40, 60, 80], 3),
        ),
    ):
        result = service.get_band_statistics(
            bucket_start=bucket_start,
            bucket_end=bucket_end,
            resolution="hour",
            band="20m",
            mode="FT8",
        )

    assert result.activity.opening_strength == pytest.approx(2.0)
    assert result.signal_quality.average_snr_db == pytest.approx(-7.5)

    cache.get.assert_called_once()
    cache.set.assert_called_once()


def test_calculate_solar_correlations_pairs_matching_buckets() -> None:
    service = StatisticsService(Mock())

    first_bucket = datetime(2026, 9, 23, 12, tzinfo=UTC)
    second_bucket = datetime(2026, 9, 23, 13, tzinfo=UTC)

    band_rollups = [
        BandRollup(
            bucket_start=first_bucket,
            band="20m",
            mode="FT8",
            observation_count=100,
            unique_sender_count=20,
            unique_receiver_count=25,
            snr_sample_count=80,
            snr_min_db=-20,
            snr_max_db=5,
            snr_avg_db=-10.0,
        ),
        BandRollup(
            bucket_start=second_bucket,
            band="20m",
            mode="FT8",
            observation_count=200,
            unique_sender_count=30,
            unique_receiver_count=35,
            snr_sample_count=160,
            snr_min_db=-18,
            snr_max_db=8,
            snr_avg_db=-5.0,
        ),
    ]

    solar_rollups = [
        SolarRollup(
            bucket_start=first_bucket,
            average_value=100.0,
        ),
        SolarRollup(
            bucket_start=second_bucket,
            average_value=200.0,
        ),
    ]

    result = service.calculate_solar_correlations(
        band_rollups=band_rollups,
        solar_rollups=solar_rollups,
    )

    assert result.activity.correlation == pytest.approx(1.0)
    assert result.activity.sample_count == 2
    assert result.signal_quality.correlation == pytest.approx(1.0)
    assert result.signal_quality.sample_count == 2


def test_calculate_solar_correlations_excludes_unmatched_buckets() -> None:
    service = StatisticsService(Mock())

    first_bucket = datetime(2026, 9, 23, 12, tzinfo=UTC)
    second_bucket = datetime(2026, 9, 23, 13, tzinfo=UTC)

    band_rollups = [
        BandRollup(
            bucket_start=first_bucket,
            band="20m",
            mode="FT8",
            observation_count=100,
            unique_sender_count=20,
            unique_receiver_count=25,
            snr_sample_count=80,
            snr_min_db=-20,
            snr_max_db=5,
            snr_avg_db=-10.0,
        ),
    ]

    solar_rollups = [
        SolarRollup(
            bucket_start=first_bucket,
            average_value=100.0,
        ),
        SolarRollup(
            bucket_start=second_bucket,
            average_value=200.0,
        ),
    ]

    result = service.calculate_solar_correlations(
        band_rollups=band_rollups,
        solar_rollups=solar_rollups,
    )

    assert result.activity.correlation is None
    assert result.activity.sample_count == 1
    assert result.signal_quality.correlation is None
    assert result.signal_quality.sample_count == 1


def test_calculate_solar_correlations_combines_radio_rows_in_same_bucket() -> None:
    bucket_start = datetime(2026, 9, 23, 12, tzinfo=UTC)

    band_rollups = [
        BandRollup(
            bucket_start=bucket_start,
            band="20m",
            mode="FT8",
            observation_count=10,
            unique_sender_count=5,
            unique_receiver_count=5,
            snr_sample_count=10,
            snr_min_db=-20,
            snr_max_db=-5,
            snr_avg_db=-10.0,
        ),
        BandRollup(
            bucket_start=bucket_start,
            band="40m",
            mode="FT8",
            observation_count=20,
            unique_sender_count=8,
            unique_receiver_count=9,
            snr_sample_count=20,
            snr_min_db=-18,
            snr_max_db=-3,
            snr_avg_db=-5.0,
        ),
    ]

    solar_rollups = [
        SolarRollup(
            bucket_start=bucket_start,
            average_value=3.0,
        ),
    ]

    service = StatisticsService(Mock())

    result = service.calculate_solar_correlations(
        band_rollups=band_rollups,
        solar_rollups=solar_rollups,
    )

    assert result.activity.sample_count == 1
    assert result.signal_quality.sample_count == 1
