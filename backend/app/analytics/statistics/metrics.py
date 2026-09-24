from dataclasses import dataclass


@dataclass(frozen=True)
class SignalQualityMetrics:
    snr_sample_count: int
    snr_coverage: float | None
    average_snr_db: float | None
    minimum_snr_db: int | None
    maximum_snr_db: int | None


@dataclass(frozen=True)
class SignalQualityRollup:
    observation_count: int
    snr_sample_count: int
    snr_avg_db: float | None
    snr_min_db: int | None
    snr_max_db: int | None


@dataclass(frozen=True)
class BandActivityMetrics:
    observation_count: int
    active_station_count: int
    baseline_observation_count: float | None
    opening_strength: float | None


@dataclass(frozen=True)
class StationActivityMetrics:
    sender_activity: int
    receiver_activity: int
    total_station_activity: int


def calculate_signal_quality(
    *,
    observation_count: int,
    snr_sample_count: int,
    snr_avg_db: float | None,
    snr_min_db: int | None,
    snr_max_db: int | None,
) -> SignalQualityMetrics:
    snr_coverage = snr_sample_count / observation_count if observation_count > 0 else None

    return SignalQualityMetrics(
        snr_sample_count=snr_sample_count,
        snr_coverage=snr_coverage,
        average_snr_db=snr_avg_db if snr_sample_count > 0 else None,
        minimum_snr_db=snr_min_db if snr_sample_count > 0 else None,
        maximum_snr_db=snr_max_db if snr_sample_count > 0 else None,
    )


def calculate_band_activity(
    *,
    observation_count: int,
    unique_sender_count: int,
    unique_receiver_count: int,
    baseline_observation_count: float | None = None,
) -> BandActivityMetrics:
    active_station_count = unique_sender_count + unique_receiver_count

    opening_strength = (
        observation_count / baseline_observation_count
        if baseline_observation_count is not None and baseline_observation_count > 0
        else None
    )

    return BandActivityMetrics(
        observation_count=observation_count,
        active_station_count=active_station_count,
        baseline_observation_count=baseline_observation_count,
        opening_strength=opening_strength,
    )


def calculate_station_activity(
    *,
    sender_activity: int,
    receiver_activity: int,
) -> StationActivityMetrics:
    return StationActivityMetrics(
        sender_activity=sender_activity,
        receiver_activity=receiver_activity,
        total_station_activity=sender_activity + receiver_activity,
    )


def combine_signal_quality(
    rollups: list[SignalQualityRollup],
) -> SignalQualityMetrics:
    observation_count = sum(rollup.observation_count for rollup in rollups)
    snr_sample_count = sum(rollup.snr_sample_count for rollup in rollups)

    weighted_snr_sum = sum(
        rollup.snr_avg_db * rollup.snr_sample_count
        for rollup in rollups
        if rollup.snr_avg_db is not None and rollup.snr_sample_count > 0
    )

    average_snr_db = weighted_snr_sum / snr_sample_count if snr_sample_count > 0 else None

    minimum_values = [rollup.snr_min_db for rollup in rollups if rollup.snr_min_db is not None]
    maximum_values = [rollup.snr_max_db for rollup in rollups if rollup.snr_max_db is not None]

    return SignalQualityMetrics(
        snr_sample_count=snr_sample_count,
        snr_coverage=(snr_sample_count / observation_count if observation_count > 0 else None),
        average_snr_db=average_snr_db,
        minimum_snr_db=min(minimum_values) if minimum_values else None,
        maximum_snr_db=max(maximum_values) if maximum_values else None,
    )


def calculate_activity_baseline(
    *,
    observation_counts: list[int],
    expected_bucket_count: int,
) -> float | None:
    if expected_bucket_count <= 0:
        return None

    return sum(observation_counts) / expected_bucket_count


@dataclass(frozen=True)
class CorrelationMetrics:
    correlation: float | None
    sample_count: int


def calculate_correlation(
    pairs: list[tuple[float, float]],
) -> CorrelationMetrics:
    sample_count = len(pairs)

    if sample_count < 2:
        return CorrelationMetrics(
            correlation=None,
            sample_count=sample_count,
        )

    solar_values = [solar_value for solar_value, _ in pairs]
    radio_values = [radio_value for _, radio_value in pairs]

    solar_mean = sum(solar_values) / sample_count
    radio_mean = sum(radio_values) / sample_count

    solar_variance = sum((value - solar_mean) ** 2 for value in solar_values)
    radio_variance = sum((value - radio_mean) ** 2 for value in radio_values)

    if solar_variance == 0 or radio_variance == 0:
        return CorrelationMetrics(
            correlation=None,
            sample_count=sample_count,
        )

    covariance = sum(
        (solar_value - solar_mean) * (radio_value - radio_mean)
        for solar_value, radio_value in pairs
    )

    correlation = covariance / (solar_variance**0.5 * radio_variance**0.5)

    return CorrelationMetrics(
        correlation=correlation,
        sample_count=sample_count,
    )
