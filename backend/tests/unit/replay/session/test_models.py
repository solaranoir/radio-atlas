from datetime import UTC, datetime, timedelta

import pytest

from app.replay.session.models import ReplaySession, ReplayState

NOW = datetime(2026, 9, 1, 11, 30, tzinfo=UTC)


def test_replay_session_starts_paused_at_start_time() -> None:
    start_time = datetime(2026, 9, 1, 12, 0, tzinfo=UTC)
    end_time = datetime(2026, 9, 1, 14, 0, tzinfo=UTC)

    session = ReplaySession.create(
        session_id="replay-123",
        start_time=start_time,
        end_time=end_time,
        now=NOW,
    )

    assert session.session_id == "replay-123"
    assert session.start_time == start_time
    assert session.end_time == end_time
    assert session.position == start_time
    assert session.state is ReplayState.PAUSED
    assert session.speed == 1.0


@pytest.mark.parametrize(
    ("start_time", "end_time"),
    [
        (
            datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
            datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        ),
        (
            datetime(2026, 9, 1, 13, 0, tzinfo=UTC),
            datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        ),
    ],
)
def test_replay_session_rejects_invalid_time_window(
    start_time: datetime,
    end_time: datetime,
) -> None:
    with pytest.raises(
        ValueError,
        match="start_time must be before end_time",
    ):
        ReplaySession.create(
            session_id="replay-123",
            start_time=start_time,
            end_time=end_time,
            now=NOW,
        )


def test_play_transitions_paused_session_to_playing() -> None:
    session = ReplaySession.create(
        session_id="replay-123",
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 14, 0, tzinfo=UTC),
        now=NOW,
    )

    session.play(now=NOW)

    assert session.state is ReplayState.PLAYING


def test_pause_transitions_playing_session_to_paused() -> None:
    session = ReplaySession.create(
        session_id="replay-123",
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 14, 0, tzinfo=UTC),
        now=NOW,
    )
    session.play(now=NOW)

    session.pause(now=NOW)

    assert session.state is ReplayState.PAUSED


def test_seek_updates_position_without_changing_state() -> None:
    session = ReplaySession.create(
        session_id="replay-123",
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 14, 0, tzinfo=UTC),
        now=NOW,
    )
    session.play(now=NOW)

    target = datetime(2026, 9, 1, 13, 15, tzinfo=UTC)

    session.seek(target, now=NOW)

    assert session.position == target
    assert session.state is ReplayState.PLAYING


@pytest.mark.parametrize(
    "target",
    [
        datetime(2026, 9, 1, 11, 59, 59, tzinfo=UTC),
        datetime(2026, 9, 1, 14, 0, 1, tzinfo=UTC),
    ],
)
def test_seek_rejects_position_outside_session_window(
    target: datetime,
) -> None:
    session = ReplaySession.create(
        session_id="replay-123",
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 14, 0, tzinfo=UTC),
        now=NOW,
    )

    with pytest.raises(
        ValueError,
        match="position must be within replay window",
    ):
        session.seek(target, now=NOW)


def test_seek_to_end_time_completes_session() -> None:
    end_time = datetime(2026, 9, 1, 14, 0, tzinfo=UTC)

    session = ReplaySession.create(
        session_id="replay-123",
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=end_time,
        now=NOW,
    )
    session.play(now=NOW)

    session.seek(end_time, now=NOW)

    assert session.position == end_time
    assert session.state is ReplayState.COMPLETED


def test_play_does_not_restart_completed_session() -> None:
    end_time = datetime(2026, 9, 1, 14, 0, tzinfo=UTC)

    session = ReplaySession.create(
        session_id="replay-123",
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=end_time,
        now=NOW,
    )
    session.seek(end_time, now=NOW)

    session.play(now=NOW)

    assert session.position == end_time
    assert session.state is ReplayState.COMPLETED


def test_seek_backward_from_completed_session_pauses_session() -> None:
    end_time = datetime(2026, 9, 1, 14, 0, tzinfo=UTC)

    session = ReplaySession.create(
        session_id="replay-123",
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=end_time,
        now=NOW,
    )
    session.seek(end_time, now=NOW)

    target = datetime(2026, 9, 1, 13, 30, tzinfo=UTC)
    session.seek(target, now=NOW)

    assert session.position == target
    assert session.state is ReplayState.PAUSED


def test_set_speed_updates_playback_speed_without_changing_state() -> None:
    session = ReplaySession.create(
        session_id="replay-123",
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 14, 0, tzinfo=UTC),
        now=NOW,
    )
    session.play(now=NOW)

    session.set_speed(4.0, now=NOW)

    assert session.speed == 4.0
    assert session.state is ReplayState.PLAYING


@pytest.mark.parametrize("speed", [0.0, -1.0])
def test_set_speed_rejects_non_positive_speed(speed: float) -> None:
    session = ReplaySession.create(
        session_id="replay-123",
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 14, 0, tzinfo=UTC),
        now=NOW,
    )

    with pytest.raises(ValueError, match="speed must be greater than zero"):
        session.set_speed(speed, now=NOW)


def test_advance_moves_position_by_elapsed_time_times_speed() -> None:
    start_time = datetime(2026, 9, 1, 12, 0, tzinfo=UTC)

    session = ReplaySession.create(
        session_id="replay-123",
        start_time=start_time,
        end_time=datetime(2026, 9, 1, 14, 0, tzinfo=UTC),
        now=NOW,
    )
    session.set_speed(2.0, now=NOW)
    session.play(now=NOW)

    session.advance(timedelta(seconds=30), now=NOW)

    assert session.position == start_time + timedelta(seconds=60)
    assert session.state is ReplayState.PLAYING


def test_advance_does_not_move_paused_session() -> None:
    start_time = datetime(2026, 9, 1, 12, 0, tzinfo=UTC)

    session = ReplaySession.create(
        session_id="replay-123",
        start_time=start_time,
        end_time=datetime(2026, 9, 1, 14, 0, tzinfo=UTC),
        now=NOW,
    )

    session.advance(timedelta(seconds=30), now=NOW)

    assert session.position == start_time
    assert session.state is ReplayState.PAUSED


def test_advance_clamps_position_to_end_and_completes_session() -> None:
    start_time = datetime(2026, 9, 1, 12, 0, tzinfo=UTC)
    end_time = datetime(2026, 9, 1, 12, 1, tzinfo=UTC)

    session = ReplaySession.create(
        session_id="replay-123",
        start_time=start_time,
        end_time=end_time,
        now=NOW,
    )
    session.set_speed(2.0, now=NOW)
    session.play(now=NOW)

    session.advance(timedelta(seconds=45), now=NOW)

    assert session.position == end_time
    assert session.state is ReplayState.COMPLETED


def test_advance_rejects_negative_elapsed_time() -> None:
    session = ReplaySession.create(
        session_id="replay-123",
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 14, 0, tzinfo=UTC),
        now=NOW,
    )
    session.play(now=NOW)

    with pytest.raises(
        ValueError,
        match="elapsed time must not be negative",
    ):
        session.advance(timedelta(seconds=-1), now=NOW)


def test_replay_session_records_creation_and_update_times() -> None:
    now = datetime(2026, 9, 1, 11, 30, tzinfo=UTC)

    session = ReplaySession.create(
        session_id="replay-123",
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 14, 0, tzinfo=UTC),
        now=now,
    )

    assert session.created_at == now
    assert session.updated_at == now


def test_play_updates_updated_at() -> None:
    session = ReplaySession.create(
        session_id="replay-123",
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 14, 0, tzinfo=UTC),
        now=NOW,
    )
    changed_at = NOW + timedelta(minutes=5)

    session.play(now=changed_at)

    assert session.state is ReplayState.PLAYING
    assert session.updated_at == changed_at


def test_pause_updates_updated_at() -> None:
    session = ReplaySession.create(
        session_id="replay-123",
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 14, 0, tzinfo=UTC),
        now=NOW,
    )
    session.play(now=NOW)

    changed_at = NOW + timedelta(minutes=5)
    session.pause(now=changed_at)

    assert session.state is ReplayState.PAUSED
    assert session.updated_at == changed_at


def test_seek_updates_updated_at() -> None:
    session = ReplaySession.create(
        session_id="replay-123",
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 14, 0, tzinfo=UTC),
        now=NOW,
    )

    changed_at = NOW + timedelta(minutes=5)
    session.seek(
        datetime(2026, 9, 1, 13, 0, tzinfo=UTC),
        now=changed_at,
    )

    assert session.position == datetime(2026, 9, 1, 13, 0, tzinfo=UTC)
    assert session.updated_at == changed_at


def test_set_speed_updates_updated_at() -> None:
    session = ReplaySession.create(
        session_id="replay-123",
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 14, 0, tzinfo=UTC),
        now=NOW,
    )

    changed_at = NOW + timedelta(minutes=5)
    session.set_speed(2.0, now=changed_at)

    assert session.speed == 2.0
    assert session.updated_at == changed_at


def test_advance_updates_updated_at() -> None:
    session = ReplaySession.create(
        session_id="replay-123",
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 14, 0, tzinfo=UTC),
        now=NOW,
    )
    session.play(now=NOW)

    changed_at = NOW + timedelta(minutes=5)
    session.advance(
        timedelta(seconds=30),
        now=changed_at,
    )

    assert session.position == datetime(2026, 9, 1, 12, 0, 30, tzinfo=UTC)
    assert session.updated_at == changed_at


def test_rejected_speed_change_does_not_update_updated_at() -> None:
    session = ReplaySession.create(
        session_id="replay-123",
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 14, 0, tzinfo=UTC),
        now=NOW,
    )

    with pytest.raises(ValueError, match="speed must be greater than zero"):
        session.set_speed(
            0.0,
            now=NOW + timedelta(minutes=5),
        )

    assert session.updated_at == NOW


def test_play_while_playing_does_not_update_timestamp() -> None:
    session = ReplaySession.create(
        session_id="test-session",
        start_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 11, 0, tzinfo=UTC),
        now=NOW,
    )
    first_play_time = datetime(2026, 9, 1, 11, 31, tzinfo=UTC)
    second_play_time = datetime(2026, 9, 1, 11, 32, tzinfo=UTC)

    session.play(now=first_play_time)
    session.play(now=second_play_time)

    assert session.state is ReplayState.PLAYING
    assert session.updated_at == first_play_time


def test_pause_while_paused_does_not_update_timestamp() -> None:
    session = ReplaySession.create(
        session_id="test-session",
        start_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 11, 0, tzinfo=UTC),
        now=NOW,
    )
    later = datetime(2026, 9, 1, 11, 31, tzinfo=UTC)

    session.pause(now=later)

    assert session.state is ReplayState.PAUSED
    assert session.updated_at == NOW


def test_pause_does_not_change_completed_session() -> None:
    session = ReplaySession.create(
        session_id="test-session",
        start_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 11, 0, tzinfo=UTC),
        now=NOW,
    )
    completed_at = datetime(2026, 9, 1, 11, 31, tzinfo=UTC)
    later = datetime(2026, 9, 1, 11, 32, tzinfo=UTC)

    session.seek(session.end_time, now=completed_at)
    session.pause(now=later)

    assert session.state is ReplayState.COMPLETED
    assert session.position == session.end_time
    assert session.updated_at == completed_at


def test_set_speed_rejects_nan() -> None:
    session = ReplaySession.create(
        session_id="test-session",
        start_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 11, 0, tzinfo=UTC),
        now=NOW,
    )

    with pytest.raises(
        ValueError,
        match="playback speed must be greater than zero",
    ):
        session.set_speed(float("nan"), now=NOW)
