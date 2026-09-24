from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.analytics.aggregation.jobs import run_hourly_aggregation
from app.analytics.statistics.service import StatisticsService
from app.infrastructure.database.models import Provider, Spot


def test_statistics_service_reads_persisted_band_rollup(
    db_session: Session,
) -> None:
    provider = Provider(
        name="statistics_band_provider",
        display_name="Statistics Band Provider",
        provider_type="spot",
    )

    db_session.add(provider)
    db_session.flush()

    db_session.add_all(
        [
            Spot(
                provider_id=provider.id,
                sequence_number=1,
                sender_callsign="KK7QEA",
                receiver_callsign="DL4JC",
                frequency_hz=14_074_000,
                band="20m",
                mode="FT8",
                snr_db=-10,
                observed_at=datetime(2026, 9, 23, 12, 5, tzinfo=UTC),
            ),
            Spot(
                provider_id=provider.id,
                sequence_number=2,
                sender_callsign="W1AW",
                receiver_callsign="EA5JLN",
                frequency_hz=14_074_000,
                band="20m",
                mode="FT8",
                snr_db=-20,
                observed_at=datetime(2026, 9, 23, 12, 20, tzinfo=UTC),
            ),
        ]
    )
    db_session.flush()

    bucket_start = datetime(2026, 9, 23, 12, tzinfo=UTC)

    run_hourly_aggregation(
        db_session,
        bucket_start=bucket_start,
    )
    db_session.flush()

    service = StatisticsService(db_session)

    rollups = service.get_band_rollups(
        start_time=bucket_start,
        end_time=datetime(2026, 9, 23, 13, tzinfo=UTC),
        resolution="hour",
        band="20m",
        mode="FT8",
    )

    assert len(rollups) == 1

    rollup = rollups[0]

    assert rollup.observation_count == 2
    assert rollup.unique_sender_count == 2
    assert rollup.unique_receiver_count == 2
    assert rollup.snr_sample_count == 2
    assert rollup.snr_min_db == -20
    assert rollup.snr_max_db == -10
    assert rollup.snr_avg_db == -15.0


def test_statistics_service_reads_persisted_station_rollups(
    db_session: Session,
) -> None:
    provider = Provider(
        name="statistics_station_provider",
        display_name="Statistics Station Provider",
        provider_type="spot",
    )

    db_session.add(provider)
    db_session.flush()

    db_session.add_all(
        [
            Spot(
                provider_id=provider.id,
                sequence_number=10,
                sender_callsign="KK7QEA",
                receiver_callsign="DL4JC",
                frequency_hz=14_074_000,
                band="20m",
                mode="FT8",
                snr_db=-10,
                observed_at=datetime(2026, 9, 23, 12, 5, tzinfo=UTC),
            ),
            Spot(
                provider_id=provider.id,
                sequence_number=11,
                sender_callsign="KK7QEA",
                receiver_callsign="EA5JLN",
                frequency_hz=14_074_000,
                band="20m",
                mode="FT8",
                snr_db=-20,
                observed_at=datetime(2026, 9, 23, 12, 20, tzinfo=UTC),
            ),
            Spot(
                provider_id=provider.id,
                sequence_number=12,
                sender_callsign="W1AW",
                receiver_callsign="KK7QEA",
                frequency_hz=14_074_000,
                band="20m",
                mode="FT8",
                snr_db=-5,
                observed_at=datetime(2026, 9, 23, 12, 40, tzinfo=UTC),
            ),
        ]
    )
    db_session.flush()

    bucket_start = datetime(2026, 9, 23, 12, tzinfo=UTC)

    run_hourly_aggregation(
        db_session,
        bucket_start=bucket_start,
    )
    db_session.flush()

    service = StatisticsService(db_session)

    rollups = service.get_station_rollups(
        start_time=bucket_start,
        end_time=datetime(2026, 9, 23, 13, tzinfo=UTC),
        resolution="hour",
        callsign="KK7QEA",
    )

    assert len(rollups) == 2

    by_direction = {rollup.direction: rollup for rollup in rollups}

    assert by_direction["sender"].observation_count == 2
    assert by_direction["sender"].unique_counterparty_count == 2
    assert by_direction["sender"].snr_avg_db == -15.0

    assert by_direction["receiver"].observation_count == 1
    assert by_direction["receiver"].unique_counterparty_count == 1
    assert by_direction["receiver"].snr_avg_db == -5.0
