from datetime import UTC, datetime
from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.analytics.statistics.metrics import (
    BandActivityMetrics,
    CorrelationMetrics,
    SignalQualityMetrics,
    StationActivityMetrics,
)
from app.analytics.statistics.service import (
    BandRollup,
    BandStatistics,
    SolarCorrelationStatistics,
    StationRollup,
    StationStatistics,
    StatisticsService,
)
from app.api.dependencies import get_statistics_service
from app.main import create_app


def _client(
    service: StatisticsService,
) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_statistics_service] = lambda: service

    return TestClient(app)


def test_get_band_statistics_returns_200_for_empty_range() -> None:
    service = Mock(spec=StatisticsService)
    service.get_band_rollups.return_value = []

    client = _client(service)

    response = client.get(
        "/api/v1/statistics/bands",
        params={
            "start_time": "2026-09-23T00:00:00Z",
            "end_time": "2026-09-24T00:00:00Z",
        },
    )

    assert response.status_code == 200
    assert response.json() == []

    service.get_band_rollups.assert_called_once()


def test_band_statistics_filters_are_forwarded() -> None:
    service = Mock(spec=StatisticsService)
    service.get_band_rollups.return_value = []

    client = _client(service)

    response = client.get(
        "/api/v1/statistics/bands",
        params={
            "start_time": "2026-09-23T00:00:00Z",
            "end_time": "2026-09-24T00:00:00Z",
            "resolution": "day",
            "band": "20m",
            "mode": "FT8",
        },
    )

    assert response.status_code == 200

    service.get_band_rollups.assert_called_once_with(
        start_time=datetime(2026, 9, 23, tzinfo=UTC),
        end_time=datetime(2026, 9, 24, tzinfo=UTC),
        resolution="day",
        band="20m",
        mode="FT8",
    )


def test_band_statistics_serializes_computed_bucket() -> None:
    service = Mock(spec=StatisticsService)

    bucket_start = datetime(2026, 9, 23, 12, tzinfo=UTC)

    service.get_band_rollups.return_value = [
        BandRollup(
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
    ]

    service.get_band_statistics.return_value = BandStatistics(
        activity=BandActivityMetrics(
            observation_count=120,
            active_station_count=70,
            baseline_observation_count=60.0,
            opening_strength=2.0,
        ),
        signal_quality=SignalQualityMetrics(
            snr_sample_count=60,
            snr_coverage=0.5,
            average_snr_db=-7.5,
            minimum_snr_db=-24,
            maximum_snr_db=8,
        ),
    )

    client = _client(service)

    response = client.get(
        "/api/v1/statistics/bands",
        params={
            "start_time": "2026-09-23T12:00:00Z",
            "end_time": "2026-09-23T13:00:00Z",
            "band": "20m",
            "mode": "FT8",
        },
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "bucket_start": "2026-09-23T12:00:00Z",
            "bucket_end": "2026-09-23T13:00:00Z",
            "resolution": "hour",
            "band": "20m",
            "mode": "FT8",
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
    ]


def test_band_statistics_rejects_invalid_time_range() -> None:
    service = Mock(spec=StatisticsService)
    client = _client(service)

    response = client.get(
        "/api/v1/statistics/bands",
        params={
            "start_time": "2026-09-24T00:00:00Z",
            "end_time": "2026-09-23T00:00:00Z",
        },
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_time_range"

    service.get_band_rollups.assert_not_called()


def test_station_statistics_filters_are_forwarded() -> None:
    service = Mock(spec=StatisticsService)
    service.get_station_rollups.return_value = []

    client = _client(service)

    response = client.get(
        "/api/v1/statistics/stations",
        params={
            "start_time": "2026-09-23T00:00:00Z",
            "end_time": "2026-09-24T00:00:00Z",
            "resolution": "day",
            "callsign": "KK7QEA",
        },
    )

    assert response.status_code == 200
    assert response.json() == []

    service.get_station_rollups.assert_called_once_with(
        start_time=datetime(2026, 9, 23, tzinfo=UTC),
        end_time=datetime(2026, 9, 24, tzinfo=UTC),
        resolution="day",
        callsign="KK7QEA",
    )


def test_station_statistics_combines_directions_and_serializes() -> None:
    service = Mock(spec=StatisticsService)

    bucket_start = datetime(2026, 9, 23, 12, tzinfo=UTC)

    service.get_station_rollups.return_value = [
        StationRollup(
            bucket_start=bucket_start,
            station_id=17,
            callsign="KK7QEA",
            direction="sender",
            observation_count=40,
            unique_counterparty_count=15,
            snr_sample_count=30,
            snr_min_db=-20,
            snr_max_db=5,
            snr_avg_db=-8.0,
        ),
        StationRollup(
            bucket_start=bucket_start,
            station_id=17,
            callsign="KK7QEA",
            direction="receiver",
            observation_count=60,
            unique_counterparty_count=22,
            snr_sample_count=50,
            snr_min_db=-18,
            snr_max_db=7,
            snr_avg_db=-6.0,
        ),
    ]

    service.calculate_station_statistics.return_value = StationStatistics(
        activity=StationActivityMetrics(
            sender_activity=40,
            receiver_activity=60,
            total_station_activity=100,
        ),
        signal_quality=SignalQualityMetrics(
            snr_sample_count=80,
            snr_coverage=0.8,
            average_snr_db=-6.75,
            minimum_snr_db=-20,
            maximum_snr_db=7,
        ),
    )

    client = _client(service)

    response = client.get(
        "/api/v1/statistics/stations",
        params={
            "start_time": "2026-09-23T12:00:00Z",
            "end_time": "2026-09-23T13:00:00Z",
            "callsign": "KK7QEA",
        },
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "start_time": "2026-09-23T12:00:00Z",
            "end_time": "2026-09-23T13:00:00Z",
            "resolution": "hour",
            "callsign": "KK7QEA",
            "activity": {
                "sender_activity": 40,
                "receiver_activity": 60,
                "total_station_activity": 100,
            },
            "signal_quality": {
                "snr_sample_count": 80,
                "snr_coverage": 0.8,
                "average_snr_db": -6.75,
                "minimum_snr_db": -20,
                "maximum_snr_db": 7,
            },
        }
    ]


def test_station_statistics_groups_rollups_by_callsign() -> None:
    service = Mock(spec=StatisticsService)

    bucket_start = datetime(2026, 9, 23, 12, tzinfo=UTC)

    service.get_station_rollups.return_value = [
        StationRollup(
            bucket_start=bucket_start,
            station_id=17,
            callsign="KK7QEA",
            direction="sender",
            observation_count=40,
            unique_counterparty_count=15,
            snr_sample_count=30,
            snr_min_db=-20,
            snr_max_db=5,
            snr_avg_db=-8.0,
        ),
        StationRollup(
            bucket_start=bucket_start,
            station_id=18,
            callsign="W1AW",
            direction="receiver",
            observation_count=25,
            unique_counterparty_count=10,
            snr_sample_count=20,
            snr_min_db=-18,
            snr_max_db=4,
            snr_avg_db=-7.0,
        ),
    ]

    service.calculate_station_statistics.side_effect = [
        StationStatistics(
            activity=StationActivityMetrics(
                sender_activity=40,
                receiver_activity=0,
                total_station_activity=40,
            ),
            signal_quality=SignalQualityMetrics(
                snr_sample_count=30,
                snr_coverage=0.75,
                average_snr_db=-8.0,
                minimum_snr_db=-20,
                maximum_snr_db=5,
            ),
        ),
        StationStatistics(
            activity=StationActivityMetrics(
                sender_activity=0,
                receiver_activity=25,
                total_station_activity=25,
            ),
            signal_quality=SignalQualityMetrics(
                snr_sample_count=20,
                snr_coverage=0.8,
                average_snr_db=-7.0,
                minimum_snr_db=-18,
                maximum_snr_db=4,
            ),
        ),
    ]

    client = _client(service)

    response = client.get(
        "/api/v1/statistics/stations",
        params={
            "start_time": "2026-09-23T12:00:00Z",
            "end_time": "2026-09-23T13:00:00Z",
        },
    )

    assert response.status_code == 200

    callsigns = {item["callsign"] for item in response.json()}

    assert callsigns == {"KK7QEA", "W1AW"}
    assert service.calculate_station_statistics.call_count == 2


def test_solar_correlation_filters_are_forwarded() -> None:
    service = Mock(spec=StatisticsService)

    service.get_solar_correlations.return_value = SolarCorrelationStatistics(
        activity=CorrelationMetrics(
            correlation=0.75,
            sample_count=12,
        ),
        signal_quality=CorrelationMetrics(
            correlation=-0.25,
            sample_count=10,
        ),
    )

    client = _client(service)

    response = client.get(
        "/api/v1/statistics/solar-correlation",
        params={
            "start_time": "2026-09-23T00:00:00Z",
            "end_time": "2026-09-24T00:00:00Z",
            "observation_type": "kp_index",
            "resolution": "hour",
            "band": "20m",
            "mode": "FT8",
        },
    )

    assert response.status_code == 200

    service.get_solar_correlations.assert_called_once_with(
        start_time=datetime(2026, 9, 23, tzinfo=UTC),
        end_time=datetime(2026, 9, 24, tzinfo=UTC),
        resolution="hour",
        observation_type="kp_index",
        band="20m",
        mode="FT8",
    )


def test_solar_correlation_serializes_results() -> None:
    service = Mock(spec=StatisticsService)

    service.get_solar_correlations.return_value = SolarCorrelationStatistics(
        activity=CorrelationMetrics(
            correlation=0.75,
            sample_count=12,
        ),
        signal_quality=CorrelationMetrics(
            correlation=None,
            sample_count=1,
        ),
    )

    client = _client(service)

    response = client.get(
        "/api/v1/statistics/solar-correlation",
        params={
            "start_time": "2026-09-23T00:00:00Z",
            "end_time": "2026-09-24T00:00:00Z",
            "observation_type": "kp_index",
            "resolution": "hour",
            "band": "20m",
            "mode": "FT8",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "start_time": "2026-09-23T00:00:00Z",
        "end_time": "2026-09-24T00:00:00Z",
        "resolution": "hour",
        "observation_type": "kp_index",
        "band": "20m",
        "mode": "FT8",
        "activity": {
            "correlation": 0.75,
            "sample_count": 12,
        },
        "signal_quality": {
            "correlation": None,
            "sample_count": 1,
        },
    }
