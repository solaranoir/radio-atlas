from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.infrastructure.database.models import (
    AnalyticsBandHourly,
    Provider,
    Spot,
)
from app.replay.streaming.models import ReplayActivityBucket
from app.replay.streaming.source import ReplayObservationSource


def test_fetch_activity_buckets_combines_band_rollups(
    db_session: Session,
) -> None:
    bucket_start = datetime(
        2026,
        9,
        20,
        14,
        0,
        tzinfo=UTC,
    )

    db_session.add_all(
        [
            AnalyticsBandHourly(
                bucket_start=bucket_start,
                band="20m",
                mode="FT8",
                observation_count=100,
                unique_sender_count=10,
                unique_receiver_count=12,
                snr_sample_count=90,
                snr_min_db=-20,
                snr_max_db=5,
                snr_avg_db=-8.0,
            ),
            AnalyticsBandHourly(
                bucket_start=bucket_start,
                band="40m",
                mode="FT8",
                observation_count=150,
                unique_sender_count=15,
                unique_receiver_count=18,
                snr_sample_count=125,
                snr_min_db=-22,
                snr_max_db=3,
                snr_avg_db=-10.0,
            ),
        ]
    )
    db_session.flush()

    source = ReplayObservationSource(db_session)

    buckets = source.fetch_activity_buckets(
        start_time=datetime(2026, 9, 20, 14, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 20, 15, 0, tzinfo=UTC),
    )

    assert buckets == [
        ReplayActivityBucket(
            bucket_start=bucket_start,
            observation_count=250,
        )
    ]


def test_fetch_page_paginates_observations_with_same_timestamp(
    db_session: Session,
) -> None:
    provider = Provider(
        name="replay_pagination_provider",
        display_name="Replay Pagination Provider",
        provider_type="spot",
    )
    db_session.add(provider)
    db_session.flush()

    observed_at = datetime(
        2026,
        9,
        20,
        14,
        30,
        tzinfo=UTC,
    )

    spots = [
        Spot(
            provider_id=provider.id,
            sequence_number=sequence_number,
            sender_callsign=f"TEST{sequence_number}",
            receiver_callsign="KK7QEA",
            frequency_hz=14_074_000,
            band="20m",
            mode="FT8",
            snr_db=-10,
            observed_at=observed_at,
        )
        for sequence_number in range(1, 4)
    ]

    db_session.add_all(spots)
    db_session.flush()

    source = ReplayObservationSource(db_session)

    first_page = source.fetch_page(
        start_time=datetime(2026, 9, 20, 14, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 20, 15, 0, tzinfo=UTC),
        limit=2,
    )

    assert [spot.id for spot in first_page.observations] == [
        spots[0].id,
        spots[1].id,
    ]
    assert first_page.next_cursor is not None

    second_page = source.fetch_page(
        start_time=datetime(2026, 9, 20, 14, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 20, 15, 0, tzinfo=UTC),
        limit=2,
        cursor_time=first_page.next_cursor.observed_at,
        cursor_id=first_page.next_cursor.observation_id,
    )

    assert [spot.id for spot in second_page.observations] == [
        spots[2].id,
    ]
    assert second_page.next_cursor is None
