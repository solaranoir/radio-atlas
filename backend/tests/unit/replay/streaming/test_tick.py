from datetime import UTC, datetime, timedelta
from unittest.mock import Mock

from app.replay.session.models import ReplaySession
from app.replay.session.service import ReplaySessionService
from app.replay.streaming.coordinator import ReplayStreamCoordinator
from app.replay.streaming.models import ReplayObservationPage
from app.replay.streaming.tick import run_replay_stream_tick


def test_tick_advances_session_and_fetches_advanced_window() -> None:
    service = Mock(spec=ReplaySessionService)
    coordinator = Mock(spec=ReplayStreamCoordinator)

    start_time = datetime(2026, 9, 1, 10, 0, tzinfo=UTC)
    end_time = datetime(2026, 9, 1, 11, 0, tzinfo=UTC)
    now = datetime(2026, 9, 30, 12, 1, 1, tzinfo=UTC)

    replay_session = ReplaySession.create(
        session_id="test-session",
        start_time=start_time,
        end_time=end_time,
        now=datetime(2026, 9, 30, 12, 0, tzinfo=UTC),
    )
    replay_session.play(
        now=datetime(2026, 9, 30, 12, 1, tzinfo=UTC),
    )

    advanced_session = ReplaySession.create(
        session_id="test-session",
        start_time=start_time,
        end_time=end_time,
        now=datetime(2026, 9, 30, 12, 0, tzinfo=UTC),
    )
    advanced_session.play(
        now=datetime(2026, 9, 30, 12, 1, tzinfo=UTC),
    )
    advanced_session.advance(
        timedelta(seconds=1),
        now=now,
    )

    service.get_session.return_value = replay_session
    service.advance_session.return_value = advanced_session

    page = ReplayObservationPage(
        observations=[],
        next_cursor=None,
    )
    coordinator.fetch_window.return_value = page

    result = run_replay_stream_tick(
        session_id="test-session",
        elapsed=timedelta(seconds=1),
        now=now,
        service=service,
        coordinator=coordinator,
    )

    assert result is not None
    assert result.position == datetime(
        2026,
        9,
        1,
        10,
        0,
        1,
        tzinfo=UTC,
    )
    assert result.page == page

    service.advance_session.assert_called_once_with(
        "test-session",
        elapsed=timedelta(seconds=1),
        now=now,
    )
    coordinator.fetch_window.assert_called_once_with(
        start_time=start_time,
        end_time=advanced_session.position,
    )


def test_tick_does_not_advance_paused_session() -> None:
    service = Mock(spec=ReplaySessionService)
    coordinator = Mock(spec=ReplayStreamCoordinator)

    replay_session = ReplaySession.create(
        session_id="test-session",
        start_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 11, 0, tzinfo=UTC),
        now=datetime(2026, 9, 30, 12, 0, tzinfo=UTC),
    )

    service.get_session.return_value = replay_session

    result = run_replay_stream_tick(
        session_id="test-session",
        elapsed=timedelta(seconds=1),
        now=datetime(2026, 9, 30, 12, 1, tzinfo=UTC),
        service=service,
        coordinator=coordinator,
    )

    assert result is None
    service.advance_session.assert_not_called()
    coordinator.fetch_window.assert_not_called()


def test_tick_returns_none_when_session_no_longer_exists() -> None:
    service = Mock(spec=ReplaySessionService)
    coordinator = Mock(spec=ReplayStreamCoordinator)

    service.get_session.return_value = None

    result = run_replay_stream_tick(
        session_id="missing-session",
        elapsed=timedelta(seconds=1),
        now=datetime(2026, 9, 30, 12, 1, tzinfo=UTC),
        service=service,
        coordinator=coordinator,
    )

    assert result is None
    service.advance_session.assert_not_called()
    coordinator.fetch_window.assert_not_called()


def test_tick_clears_prefetch_when_position_changed() -> None:
    service = Mock(spec=ReplaySessionService)
    coordinator = Mock(spec=ReplayStreamCoordinator)

    replay_session = ReplaySession.create(
        session_id="test-session",
        start_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 11, 0, tzinfo=UTC),
        now=datetime(2026, 9, 30, 12, 0, tzinfo=UTC),
    )
    replay_session.seek(
        datetime(2026, 9, 1, 10, 30, tzinfo=UTC),
        now=datetime(2026, 9, 30, 12, 1, tzinfo=UTC),
    )

    service.get_session.return_value = replay_session

    result = run_replay_stream_tick(
        session_id="test-session",
        elapsed=timedelta(seconds=1),
        now=datetime(2026, 9, 30, 12, 2, tzinfo=UTC),
        service=service,
        coordinator=coordinator,
        expected_position=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
    )

    assert result is None
    coordinator.handle_seek.assert_called_once_with()
    service.advance_session.assert_not_called()
