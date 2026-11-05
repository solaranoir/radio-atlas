from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.infrastructure.database.models import (
    AnalyticsBandDaily,
    AnalyticsBandHourly,
    AnalyticsStationHourly,
    Provider,
    Spot,
)
from app.ingestion.retention import roll_up_day_once, run_spot_retention
from app.timeline.source import TimelineSource

pytestmark = pytest.mark.integration

BAND = "retention-test"
NOW = datetime(2031, 5, 20, 9, 30, tzinfo=UTC)
CUTOFF = datetime(2031, 5, 6, tzinfo=UTC)  # 14 days before the start of NOW's day
OLD_DAY_1 = datetime(2031, 4, 30, tzinfo=UTC)
OLD_DAY_2 = datetime(2031, 5, 1, tzinfo=UTC)
RECENT = datetime(2031, 5, 19, 12, tzinfo=UTC)


@pytest.fixture
def provider(db_session: Session) -> Provider:
    provider = Provider(name=f"retention-{uuid4()}", display_name="Retention", provider_type="spot")
    db_session.add(provider)
    db_session.flush()
    return provider


def _add_spots(session: Session, provider: Provider, times: list[datetime]) -> None:
    start = session.execute(select(func.count(Spot.id))).scalar_one()
    session.add_all(
        Spot(
            provider_id=provider.id,
            sequence_number=start + index,
            sender_callsign=f"RT{index % 3}",
            receiver_callsign="RX1",
            band=BAND,
            mode="FT8",
            snr_db=-10,
            observed_at=at,
        )
        for index, at in enumerate(times)
    )
    session.flush()


def _spot_count(session: Session) -> int:
    return session.execute(select(func.count(Spot.id)).where(Spot.band == BAND)).scalar_one()


def _hourly(session: Session) -> dict[datetime, int]:
    rows = session.execute(
        select(AnalyticsBandHourly.bucket_start, AnalyticsBandHourly.observation_count).where(
            AnalyticsBandHourly.band == BAND
        )
    )
    return {bucket: count for bucket, count in rows}


def _daily(session: Session) -> dict[datetime, int]:
    rows = session.execute(
        select(AnalyticsBandDaily.bucket_start, AnalyticsBandDaily.observation_count).where(
            AnalyticsBandDaily.band == BAND
        )
    )
    return {bucket: count for bucket, count in rows}


def test_retention_rolls_up_then_deletes_only_expired_days(
    db_session: Session, provider: Provider
) -> None:
    old = [
        OLD_DAY_1 + timedelta(hours=3, minutes=5),
        OLD_DAY_1 + timedelta(hours=3, minutes=40),
        OLD_DAY_1 + timedelta(hours=7),
        OLD_DAY_2 + timedelta(hours=23, minutes=59),
    ]
    recent = [RECENT, RECENT + timedelta(minutes=1)]
    _add_spots(db_session, provider, old + recent)

    result = run_spot_retention(db_session, now=NOW, retention_days=14, batch_size=2)

    assert result.cutoff == CUTOFF
    assert result.spots_deleted >= len(old)
    assert _spot_count(db_session) == len(recent)
    assert (
        db_session.execute(select(func.min(Spot.observed_at)).where(Spot.band == BAND)).scalar_one()
        == RECENT
    )

    # Rollups for the deleted days were rebuilt before deletion.
    assert _hourly(db_session) == {
        OLD_DAY_1 + timedelta(hours=3): 2,
        OLD_DAY_1 + timedelta(hours=7): 1,
        OLD_DAY_2 + timedelta(hours=23): 1,
    }
    assert _daily(db_session) == {OLD_DAY_1: 3, OLD_DAY_2: 1}
    station_rows = db_session.execute(
        select(func.count(AnalyticsStationHourly.id)).where(
            AnalyticsStationHourly.callsign.in_(["RT0", "RT1", "RT2"]),
            AnalyticsStationHourly.bucket_start < CUTOFF,
        )
    ).scalar_one()
    assert station_rows > 0

    # The timeline still reaches back to the rolled-up history.
    first, _ = TimelineSource(db_session).history_bounds()
    assert first is not None
    assert first <= OLD_DAY_1 + timedelta(hours=3)


def test_retention_is_idempotent_and_handles_late_arrivals(
    db_session: Session, provider: Provider
) -> None:
    _add_spots(db_session, provider, [OLD_DAY_1 + timedelta(hours=1)])
    run_spot_retention(db_session, now=NOW, retention_days=14)
    assert _hourly(db_session) == {OLD_DAY_1 + timedelta(hours=1): 1}

    rerun = run_spot_retention(db_session, now=NOW, retention_days=14)
    assert rerun.days_processed == 0
    assert rerun.spots_deleted == 0

    # A spot arriving late for an already-retained day is deleted, and the
    # day is not re-aggregated: recomputing from the remaining raw spots would
    # overwrite the rollup with a lower count.
    _add_spots(db_session, provider, [OLD_DAY_1 + timedelta(hours=1, minutes=30)])
    late = run_spot_retention(db_session, now=NOW, retention_days=14)

    assert late.spots_deleted == 1
    assert _spot_count(db_session) == 0
    assert _hourly(db_session) == {OLD_DAY_1 + timedelta(hours=1): 1}
    assert _daily(db_session) == {OLD_DAY_1: 1}


def test_interrupted_deletion_resumes_without_undercounting(
    db_session: Session, provider: Provider
) -> None:
    times = [OLD_DAY_1 + timedelta(hours=2, minutes=minute) for minute in range(5)]
    _add_spots(db_session, provider, times)

    # Simulate a run that rolled up and marked the day, then stopped after
    # deleting only some of its spots.
    assert roll_up_day_once(db_session, OLD_DAY_1)
    db_session.flush()
    partial = select(Spot.id).where(Spot.band == BAND).limit(2)
    db_session.execute(delete(Spot).where(Spot.id.in_(partial)))
    db_session.flush()

    run_spot_retention(db_session, now=NOW, retention_days=14)

    assert _spot_count(db_session) == 0
    assert _hourly(db_session) == {OLD_DAY_1 + timedelta(hours=2): 5}
    assert _daily(db_session) == {OLD_DAY_1: 5}
    assert not roll_up_day_once(db_session, OLD_DAY_1)


def test_retention_without_expired_spots_does_nothing(
    db_session: Session, provider: Provider
) -> None:
    _add_spots(db_session, provider, [RECENT])

    result = run_spot_retention(db_session, now=NOW, retention_days=14)

    assert _spot_count(db_session) == 1
    assert result.cutoff == CUTOFF
