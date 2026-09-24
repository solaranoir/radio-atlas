import pytest

from app.analytics.statistics.metrics import (
    SignalQualityRollup,
    calculate_activity_baseline,
    calculate_band_activity,
    calculate_correlation,
    calculate_signal_quality,
    calculate_station_activity,
    combine_signal_quality,
)


def test_calculate_signal_quality() -> None:
    result = calculate_signal_quality(
        observation_count=10,
        snr_sample_count=5,
        snr_avg_db=-8.0,
        snr_min_db=-20,
        snr_max_db=4,
    )

    assert result.snr_sample_count == 5
    assert result.snr_coverage == pytest.approx(0.5)
    assert result.average_snr_db == pytest.approx(-8.0)
    assert result.minimum_snr_db == -20
    assert result.maximum_snr_db == 4


def test_calculate_signal_quality_without_snr_samples() -> None:
    result = calculate_signal_quality(
        observation_count=10,
        snr_sample_count=0,
        snr_avg_db=None,
        snr_min_db=None,
        snr_max_db=None,
    )

    assert result.snr_sample_count == 0
    assert result.snr_coverage == pytest.approx(0.0)
    assert result.average_snr_db is None
    assert result.minimum_snr_db is None
    assert result.maximum_snr_db is None


def test_calculate_signal_quality_without_observations() -> None:
    result = calculate_signal_quality(
        observation_count=0,
        snr_sample_count=0,
        snr_avg_db=None,
        snr_min_db=None,
        snr_max_db=None,
    )

    assert result.snr_coverage is None


def test_calculate_band_activity() -> None:
    result = calculate_band_activity(
        observation_count=120,
        unique_sender_count=30,
        unique_receiver_count=40,
        baseline_observation_count=60.0,
    )

    assert result.observation_count == 120
    assert result.active_station_count == 70
    assert result.baseline_observation_count == pytest.approx(60.0)
    assert result.opening_strength == pytest.approx(2.0)


def test_calculate_band_activity_without_baseline() -> None:
    result = calculate_band_activity(
        observation_count=20,
        unique_sender_count=8,
        unique_receiver_count=10,
    )

    assert result.active_station_count == 18
    assert result.baseline_observation_count is None
    assert result.opening_strength is None


def test_calculate_band_activity_with_zero_baseline() -> None:
    result = calculate_band_activity(
        observation_count=20,
        unique_sender_count=8,
        unique_receiver_count=10,
        baseline_observation_count=0.0,
    )

    assert result.baseline_observation_count == pytest.approx(0.0)
    assert result.opening_strength is None


def test_calculate_station_activity() -> None:
    result = calculate_station_activity(
        sender_activity=35,
        receiver_activity=45,
    )

    assert result.sender_activity == 35
    assert result.receiver_activity == 45
    assert result.total_station_activity == 80


def test_calculate_station_activity_with_no_activity() -> None:
    result = calculate_station_activity(
        sender_activity=0,
        receiver_activity=0,
    )

    assert result.sender_activity == 0
    assert result.receiver_activity == 0
    assert result.total_station_activity == 0


def test_combine_signal_quality_weights_average_by_sample_count() -> None:
    rollups = [
        SignalQualityRollup(
            observation_count=10,
            snr_sample_count=2,
            snr_avg_db=-10.0,
            snr_min_db=-15,
            snr_max_db=-5,
        ),
        SignalQualityRollup(
            observation_count=20,
            snr_sample_count=8,
            snr_avg_db=0.0,
            snr_min_db=-8,
            snr_max_db=6,
        ),
    ]

    result = combine_signal_quality(rollups)

    assert result.snr_sample_count == 10
    assert result.snr_coverage == pytest.approx(10 / 30)
    assert result.average_snr_db == pytest.approx(-2.0)
    assert result.minimum_snr_db == -15
    assert result.maximum_snr_db == 6


def test_calculate_activity_baseline_counts_missing_buckets_as_zero() -> None:
    result = calculate_activity_baseline(
        observation_counts=[12, 18, 30],
        expected_bucket_count=4,
    )

    assert result == pytest.approx(15.0)


def test_calculate_correlation_returns_perfect_positive_correlation() -> None:
    result = calculate_correlation(
        [
            (1.0, 10.0),
            (2.0, 20.0),
            (3.0, 30.0),
        ]
    )

    assert result.correlation == pytest.approx(1.0)
    assert result.sample_count == 3


def test_calculate_correlation_is_undefined_with_one_pair() -> None:
    result = calculate_correlation(
        [
            (4.0, 120.0),
        ]
    )

    assert result.correlation is None
    assert result.sample_count == 1


def test_calculate_correlation_is_undefined_with_zero_variance() -> None:
    result = calculate_correlation(
        [
            (3.0, 100.0),
            (3.0, 120.0),
            (3.0, 140.0),
        ]
    )

    assert result.correlation is None
    assert result.sample_count == 3
