import pytest

from datetime import UTC, datetime

from app.replay.streaming.queries import (
    build_replay_activity_query,
    build_replay_observations_query,
)

def test_replay_query_uses_half_open_window_and_chronological_order() -> None:
    start_time = datetime(
        2026,
        9,
        1,
        12,
        0,
        tzinfo=UTC,
    )
    end_time = datetime(
        2026,
        9,
        1,
        13,
        0,
        tzinfo=UTC,
    )

    query = build_replay_observations_query(
        start_time=start_time,
        end_time=end_time,
    )

    compiled = str(query)

    assert "spots.observed_at >=" in compiled
    assert "spots.observed_at <" in compiled
    assert "spots.observed_at <=" not in compiled
    assert "ORDER BY spots.observed_at ASC, spots.id ASC" in compiled

    params = query.compile().params

    assert start_time in params.values()
    assert end_time in params.values()

def test_replay_query_applies_keyset_cursor() -> None:
    start_time = datetime(
        2026,
        9,
        1,
        12,
        0,
        tzinfo=UTC,
    )
    end_time = datetime(
        2026,
        9,
        1,
        13,
        0,
        tzinfo=UTC,
    )
    cursor_time = datetime(
        2026,
        9,
        1,
        12,
        30,
        tzinfo=UTC,
    )

    query = build_replay_observations_query(
        start_time=start_time,
        end_time=end_time,
        cursor_time=cursor_time,
        cursor_id=42,
    )

    compiled = str(query)

    assert "spots.observed_at >" in compiled
    assert "spots.id >" in compiled

    params = query.compile().params

    assert cursor_time in params.values()
    assert 42 in params.values()

@pytest.mark.parametrize(
    ("cursor_time", "cursor_id"),
    [
        (datetime(2026, 9, 1, 12, 30, tzinfo=UTC), None),
        (None, 42),
    ],
)
def test_replay_query_rejects_incomplete_cursor(
    cursor_time: datetime | None,
    cursor_id: int | None,
) -> None:
    with pytest.raises(ValueError, match="cursor_time and cursor_id"):
        build_replay_observations_query(
            start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
            end_time=datetime(2026, 9, 1, 13, 0, tzinfo=UTC),
            cursor_time=cursor_time,
            cursor_id=cursor_id,
        )

def test_replay_activity_query_uses_hourly_rollups() -> None:
    start_time = datetime(
        2026,
        9,
        1,
        12,
        0,
        tzinfo=UTC,
    )
    end_time = datetime(
        2026,
        9,
        1,
        15,
        0,
        tzinfo=UTC,
    )

    query = build_replay_activity_query(
        start_time=start_time,
        end_time=end_time,
    )

    compiled = str(query)

    assert "analytics_band_hourly" in compiled
    assert "bucket_start >=" in compiled
    assert "bucket_start <" in compiled
    assert "sum(analytics_band_hourly.observation_count)" in compiled.lower()
    assert "GROUP BY analytics_band_hourly.bucket_start" in compiled
    assert "ORDER BY analytics_band_hourly.bucket_start" in compiled
