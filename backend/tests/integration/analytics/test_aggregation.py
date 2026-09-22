from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.aggregation.jobs import (
    run_daily_aggregation,
    run_hourly_aggregation,
    run_hourly_backfill,
)
from app.infrastructure.database.models import (
    AnalyticsBandDaily,
    AnalyticsBandHourly,
    AnalyticsStationHourly,
    Provider,
    Spot,
)


def test_hourly_band_aggregation_persists_accurate_metrics(
    db_session: Session,
) -> None:
    provider = Provider(
        name="aggregation_test_provider",
        display_name="Aggregation Test Provider",
        provider_type="spot",
    )

    db_session.add(provider)
    db_session.flush()

    spots = [
        Spot(
            provider_id=provider.id,
            sequence_number=1,
            sender_callsign="KK7QEA",
            receiver_callsign="DL4JC",
            frequency_hz=14_074_000,
            band="20m",
            mode="FT8",
            snr_db=-10,
            observed_at=datetime(2026, 9, 19, 14, 5, tzinfo=UTC),
        ),
        Spot(
            provider_id=provider.id,
            sequence_number=2,
            sender_callsign="KK7QEA",
            receiver_callsign="EA5JLN",
            frequency_hz=14_074_000,
            band="20m",
            mode="FT8",
            snr_db=-20,
            observed_at=datetime(2026, 9, 19, 14, 20, tzinfo=UTC),
        ),
        Spot(
            provider_id=provider.id,
            sequence_number=3,
            sender_callsign="W1AW",
            receiver_callsign="DL4JC",
            frequency_hz=14_074_000,
            band="20m",
            mode="FT8",
            snr_db=None,
            observed_at=datetime(2026, 9, 19, 14, 45, tzinfo=UTC),
        ),
    ]

    db_session.add_all(spots)
    db_session.flush()

    run_hourly_aggregation(
        db_session,
        bucket_start=datetime(2026, 9, 19, 14, 37, tzinfo=UTC),
    )
    db_session.flush()

    rollup = db_session.scalar(
        select(AnalyticsBandHourly).where(
            AnalyticsBandHourly.bucket_start == datetime(2026, 9, 19, 14, 0, tzinfo=UTC),
            AnalyticsBandHourly.band == "20m",
            AnalyticsBandHourly.mode == "FT8",
        )
    )

    assert rollup is not None
    assert rollup.observation_count == 3
    assert rollup.unique_sender_count == 2
    assert rollup.unique_receiver_count == 2
    assert rollup.snr_sample_count == 2
    assert rollup.snr_min_db == -20
    assert rollup.snr_max_db == -10
    assert rollup.snr_avg_db == -15.0


def test_hourly_band_aggregation_is_idempotent(
    db_session: Session,
) -> None:
    provider = Provider(
        name="aggregation_idempotency_provider",
        display_name="Aggregation Idempotency Provider",
        provider_type="spot",
    )

    db_session.add(provider)
    db_session.flush()

    db_session.add(
        Spot(
            provider_id=provider.id,
            sequence_number=100,
            sender_callsign="KK7QEA",
            receiver_callsign="DL4JC",
            frequency_hz=14_074_000,
            band="20m",
            mode="FT8",
            snr_db=-12,
            observed_at=datetime(2026, 9, 19, 14, 15, tzinfo=UTC),
        )
    )
    db_session.flush()

    bucket_start = datetime(2026, 9, 19, 14, 0, tzinfo=UTC)

    run_hourly_aggregation(
        db_session,
        bucket_start=bucket_start,
    )
    db_session.flush()

    run_hourly_aggregation(
        db_session,
        bucket_start=bucket_start,
    )
    db_session.flush()

    rollups = db_session.scalars(
        select(AnalyticsBandHourly).where(
            AnalyticsBandHourly.bucket_start == bucket_start,
            AnalyticsBandHourly.band == "20m",
            AnalyticsBandHourly.mode == "FT8",
        )
    ).all()

    assert len(rollups) == 1
    assert rollups[0].observation_count == 1
    assert rollups[0].snr_sample_count == 1
    assert rollups[0].snr_avg_db == -12.0


def test_hourly_band_aggregation_updates_for_late_arriving_spot(
    db_session: Session,
) -> None:
    provider = Provider(
        name="aggregation_late_arrival_provider",
        display_name="Aggregation Late Arrival Provider",
        provider_type="spot",
    )

    db_session.add(provider)
    db_session.flush()

    bucket_start = datetime(2026, 9, 19, 14, 0, tzinfo=UTC)

    db_session.add(
        Spot(
            provider_id=provider.id,
            sequence_number=200,
            sender_callsign="KK7QEA",
            receiver_callsign="DL4JC",
            frequency_hz=14_074_000,
            band="20m",
            mode="FT8",
            snr_db=-10,
            observed_at=datetime(2026, 9, 19, 14, 10, tzinfo=UTC),
        )
    )
    db_session.flush()

    run_hourly_aggregation(
        db_session,
        bucket_start=bucket_start,
    )
    db_session.flush()

    db_session.add(
        Spot(
            provider_id=provider.id,
            sequence_number=201,
            sender_callsign="W1AW",
            receiver_callsign="EA5JLN",
            frequency_hz=14_074_000,
            band="20m",
            mode="FT8",
            snr_db=-20,
            observed_at=datetime(2026, 9, 19, 14, 50, tzinfo=UTC),
        )
    )
    db_session.flush()

    run_hourly_aggregation(
        db_session,
        bucket_start=bucket_start,
    )
    db_session.flush()

    rollups = db_session.scalars(
        select(AnalyticsBandHourly).where(
            AnalyticsBandHourly.bucket_start == bucket_start,
            AnalyticsBandHourly.band == "20m",
            AnalyticsBandHourly.mode == "FT8",
        )
    ).all()

    assert len(rollups) == 1

    rollup = rollups[0]

    assert rollup.observation_count == 2
    assert rollup.unique_sender_count == 2
    assert rollup.unique_receiver_count == 2
    assert rollup.snr_sample_count == 2
    assert rollup.snr_min_db == -20
    assert rollup.snr_max_db == -10
    assert rollup.snr_avg_db == -15.0


def test_hourly_station_aggregation_persists_accurate_metrics(
    db_session: Session,
) -> None:
    provider = Provider(
        name="station_aggregation_test_provider",
        display_name="Station Aggregation Test Provider",
        provider_type="spot",
    )

    db_session.add(provider)
    db_session.flush()

    spots = [
        Spot(
            provider_id=provider.id,
            sequence_number=300,
            sender_callsign="KK7QEA",
            receiver_callsign="DL4JC",
            frequency_hz=14_074_000,
            band="20m",
            mode="FT8",
            snr_db=-8,
            observed_at=datetime(2026, 9, 19, 14, 5, tzinfo=UTC),
        ),
        Spot(
            provider_id=provider.id,
            sequence_number=301,
            sender_callsign="KK7QEA",
            receiver_callsign="EA5JLN",
            frequency_hz=14_074_000,
            band="20m",
            mode="FT8",
            snr_db=-18,
            observed_at=datetime(2026, 9, 19, 14, 20, tzinfo=UTC),
        ),
        Spot(
            provider_id=provider.id,
            sequence_number=302,
            sender_callsign="KK7QEA",
            receiver_callsign="DL4JC",
            frequency_hz=7_074_000,
            band="40m",
            mode="FT8",
            snr_db=None,
            observed_at=datetime(2026, 9, 19, 14, 45, tzinfo=UTC),
        ),
    ]

    db_session.add_all(spots)
    db_session.flush()

    bucket_start = datetime(2026, 9, 19, 14, 0, tzinfo=UTC)

    run_hourly_aggregation(
        db_session,
        bucket_start=bucket_start,
    )
    db_session.flush()

    rollup = db_session.scalar(
        select(AnalyticsStationHourly).where(
            AnalyticsStationHourly.bucket_start == bucket_start,
            AnalyticsStationHourly.callsign == "KK7QEA",
            AnalyticsStationHourly.direction == "sender",
        )
    )

    assert rollup is not None
    assert rollup.observation_count == 3
    assert rollup.unique_counterparty_count == 2
    assert rollup.snr_sample_count == 2
    assert rollup.snr_min_db == -18
    assert rollup.snr_max_db == -8
    assert rollup.snr_avg_db == -13.0


def test_hourly_backfill_persists_multiple_buckets(
    db_session: Session,
) -> None:
    provider = Provider(
        name="aggregation_backfill_provider",
        display_name="Aggregation Backfill Provider",
        provider_type="spot",
    )

    db_session.add(provider)
    db_session.flush()

    db_session.add_all(
        [
            Spot(
                provider_id=provider.id,
                sequence_number=400,
                sender_callsign="KK7QEA",
                receiver_callsign="DL4JC",
                frequency_hz=14_074_000,
                band="20m",
                mode="FT8",
                snr_db=-10,
                observed_at=datetime(2026, 9, 19, 10, 15, tzinfo=UTC),
            ),
            Spot(
                provider_id=provider.id,
                sequence_number=401,
                sender_callsign="W1AW",
                receiver_callsign="EA5JLN",
                frequency_hz=14_074_000,
                band="20m",
                mode="FT8",
                snr_db=-20,
                observed_at=datetime(2026, 9, 19, 11, 15, tzinfo=UTC),
            ),
        ]
    )
    db_session.flush()

    run_hourly_backfill(
        db_session,
        start_time=datetime(2026, 9, 19, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 19, 12, 0, tzinfo=UTC),
    )
    db_session.flush()

    rollups = db_session.scalars(
        select(AnalyticsBandHourly)
        .where(
            AnalyticsBandHourly.band == "20m",
            AnalyticsBandHourly.mode == "FT8",
        )
        .order_by(AnalyticsBandHourly.bucket_start)
    ).all()

    assert len(rollups) == 2

    assert rollups[0].bucket_start == datetime(2026, 9, 19, 10, 0, tzinfo=UTC)
    assert rollups[0].observation_count == 1
    assert rollups[0].snr_avg_db == -10.0

    assert rollups[1].bucket_start == datetime(2026, 9, 19, 11, 0, tzinfo=UTC)
    assert rollups[1].observation_count == 1
    assert rollups[1].snr_avg_db == -20.0


def test_daily_band_aggregation_persists_accurate_metrics(
    db_session: Session,
) -> None:
    provider = Provider(
        name="daily_aggregation_test_provider",
        display_name="Daily Aggregation Test Provider",
        provider_type="spot",
    )

    db_session.add(provider)
    db_session.flush()

    db_session.add_all(
        [
            Spot(
                provider_id=provider.id,
                sequence_number=500,
                sender_callsign="KK7QEA",
                receiver_callsign="DL4JC",
                frequency_hz=14_074_000,
                band="20m",
                mode="FT8",
                snr_db=-10,
                observed_at=datetime(2026, 9, 19, 2, 15, tzinfo=UTC),
            ),
            Spot(
                provider_id=provider.id,
                sequence_number=501,
                sender_callsign="KK7QEA",
                receiver_callsign="EA5JLN",
                frequency_hz=14_074_000,
                band="20m",
                mode="FT8",
                snr_db=-20,
                observed_at=datetime(2026, 9, 19, 18, 30, tzinfo=UTC),
            ),
            Spot(
                provider_id=provider.id,
                sequence_number=502,
                sender_callsign="W1AW",
                receiver_callsign="DL4JC",
                frequency_hz=14_074_000,
                band="20m",
                mode="FT8",
                snr_db=None,
                observed_at=datetime(2026, 9, 19, 23, 45, tzinfo=UTC),
            ),
        ]
    )
    db_session.flush()

    run_daily_aggregation(
        db_session,
        bucket_start=datetime(2026, 9, 19, 14, 37, tzinfo=UTC),
    )
    db_session.flush()

    rollup = db_session.scalar(
        select(AnalyticsBandDaily).where(
            AnalyticsBandDaily.bucket_start == datetime(2026, 9, 19, 0, 0, tzinfo=UTC),
            AnalyticsBandDaily.band == "20m",
            AnalyticsBandDaily.mode == "FT8",
        )
    )

    assert rollup is not None
    assert rollup.observation_count == 3
    assert rollup.unique_sender_count == 2
    assert rollup.unique_receiver_count == 2
    assert rollup.snr_sample_count == 2
    assert rollup.snr_min_db == -20
    assert rollup.snr_max_db == -10
    assert rollup.snr_avg_db == -15.0


def test_hourly_aggregation_excludes_null_band_only_from_band_rollups(
    db_session: Session,
) -> None:
    provider = Provider(
        name="null_band_aggregation_provider",
        display_name="Null Band Aggregation Provider",
        provider_type="spot",
    )

    db_session.add(provider)
    db_session.flush()

    bucket_start = datetime(2026, 9, 19, 14, 0, tzinfo=UTC)

    db_session.add(
        Spot(
            provider_id=provider.id,
            sequence_number=600,
            sender_callsign="KK7QEA",
            receiver_callsign="DL4JC",
            frequency_hz=None,
            band=None,
            mode="FT8",
            snr_db=-7,
            observed_at=datetime(2026, 9, 19, 14, 20, tzinfo=UTC),
        )
    )
    db_session.flush()

    run_hourly_aggregation(
        db_session,
        bucket_start=bucket_start,
    )
    db_session.flush()

    band_rollups = db_session.scalars(
        select(AnalyticsBandHourly).where(
            AnalyticsBandHourly.bucket_start == bucket_start,
        )
    ).all()

    station_rollup = db_session.scalar(
        select(AnalyticsStationHourly).where(
            AnalyticsStationHourly.bucket_start == bucket_start,
            AnalyticsStationHourly.callsign == "KK7QEA",
            AnalyticsStationHourly.direction == "sender",
        )
    )

    assert band_rollups == []

    assert station_rollup is not None
    assert station_rollup.observation_count == 1
    assert station_rollup.unique_counterparty_count == 1
    assert station_rollup.snr_sample_count == 1
    assert station_rollup.snr_avg_db == -7.0
