from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from app.replay.session.models import ReplaySession, ReplayState

START = datetime(2026, 9, 1, 10, tzinfo=UTC)
NOW = datetime(2026, 9, 30, 12, tzinfo=UTC)


@pytest.fixture
def replay_session() -> ReplaySession:
    return ReplaySession.create(
        session_id="matrix-session",
        start_time=START,
        end_time=START + timedelta(seconds=60),
        now=NOW,
    )


@pytest.mark.parametrize("speed", [0.25, 0.5, 1.0, 2.0, 4.0, 16.0])
def test_fractional_ticks_accumulate_and_finish_exactly(
    replay_session: ReplaySession, speed: float
) -> None:
    replay_session.set_speed(speed, now=NOW)
    replay_session.play(now=NOW)
    for tick in range(1, 9):
        replay_session.advance(timedelta(milliseconds=125), now=NOW + timedelta(seconds=tick))
        assert replay_session.position == START + timedelta(seconds=tick * 0.125 * speed)
    replay_session.advance(timedelta(seconds=240), now=NOW + timedelta(seconds=9))
    assert replay_session.position == replay_session.end_time
    assert replay_session.state is ReplayState.COMPLETED
    completed = replace(replay_session)
    replay_session.advance(timedelta(seconds=10), now=NOW + timedelta(seconds=10))
    assert replay_session == completed


@pytest.mark.parametrize("state", list(ReplayState))
@pytest.mark.parametrize("offset_us", [0, 1, 30_123_456, 59_999_999, 60_000_000])
def test_seek_preserves_microsecond_precision_and_transition_contract(
    replay_session: ReplaySession, state: ReplayState, offset_us: int
) -> None:
    replay_session.state = state
    replay_session.position = replay_session.end_time if state is ReplayState.COMPLETED else START
    target = START + timedelta(microseconds=offset_us)
    replay_session.seek(target, now=NOW + timedelta(seconds=1))
    expected = ReplayState.PAUSED if state is ReplayState.COMPLETED else state
    if target == replay_session.end_time:
        expected = ReplayState.COMPLETED
    assert replay_session.position == target
    assert replay_session.state is expected
    assert replay_session.updated_at == NOW + timedelta(seconds=1)


@pytest.mark.parametrize("state", list(ReplayState))
@pytest.mark.parametrize("offset_us", [-1, 60_000_001])
def test_rejected_seek_is_atomic(
    replay_session: ReplaySession, state: ReplayState, offset_us: int
) -> None:
    replay_session.state = state
    before = replace(replay_session)
    with pytest.raises(ValueError, match="within replay window"):
        replay_session.seek(
            START + timedelta(microseconds=offset_us), now=NOW + timedelta(seconds=1)
        )
    assert replay_session == before


def test_speed_change_pause_and_resume_apply_only_to_future_ticks(
    replay_session: ReplaySession,
) -> None:
    replay_session.play(now=NOW)
    replay_session.advance(timedelta(seconds=2), now=NOW)
    replay_session.set_speed(0.5, now=NOW)
    assert replay_session.position == START + timedelta(seconds=2)
    replay_session.advance(timedelta(seconds=2), now=NOW)
    replay_session.pause(now=NOW)
    paused = replace(replay_session)
    replay_session.advance(timedelta(hours=1), now=NOW + timedelta(hours=1))
    assert replay_session == paused
    replay_session.set_speed(4.0, now=NOW)
    replay_session.play(now=NOW)
    replay_session.advance(timedelta(seconds=2), now=NOW)
    assert replay_session.position == START + timedelta(seconds=11)
