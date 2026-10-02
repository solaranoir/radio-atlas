from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

from app.replay.session.models import ReplaySession
from app.replay.streaming.models import ReplayCursor, ReplayObservationPage
from app.replay.streaming.coordinator import ReplayStreamCoordinator

def test_advance_fetches_observations_for_advanced_window() -> None:
    replay_session = ReplaySession.create(
        session_id="test-session",
        start_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 11, 0, tzinfo=UTC),
        now=datetime(2026, 9, 30, 12, 0, tzinfo=UTC),
    )
    replay_session.play(
        now=datetime(2026, 9, 30, 12, 1, tzinfo=UTC),
    )

    prefetcher = MagicMock()
    page = ReplayObservationPage(
        observations=[],
        next_cursor=None,
    )
    prefetcher.fetch_next.return_value = page

    coordinator = ReplayStreamCoordinator(
        prefetcher=prefetcher,
    )

    result = coordinator.advance(
        replay_session,
        elapsed=timedelta(seconds=10),
        now=datetime(2026, 9, 30, 12, 1, 10, tzinfo=UTC),
    )

    assert result == page
    assert replay_session.position == datetime(
        2026,
        9,
        1,
        10,
        0,
        10,
        tzinfo=UTC,
    )

    prefetcher.fetch_next.assert_called_once_with(
        start_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 10, 0, 10, tzinfo=UTC),
    )

def test_advance_does_not_fetch_when_session_is_paused() -> None:
    replay_session = ReplaySession.create(
        session_id="test-session",
        start_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 11, 0, tzinfo=UTC),
        now=datetime(2026, 9, 30, 12, 0, tzinfo=UTC),
    )

    prefetcher = MagicMock()

    coordinator = ReplayStreamCoordinator(
        prefetcher=prefetcher,
    )

    result = coordinator.advance(
        replay_session,
        elapsed=timedelta(seconds=10),
        now=datetime(2026, 9, 30, 12, 0, 10, tzinfo=UTC),
    )

    assert result == ReplayObservationPage(
        observations=[],
        next_cursor=None,
    )
    assert replay_session.position == replay_session.start_time
    prefetcher.fetch_next.assert_not_called()

def test_advance_clamps_fetch_window_at_session_end() -> None:
    replay_session = ReplaySession.create(
        session_id="test-session",
        start_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 10, 0, 15, tzinfo=UTC),
        now=datetime(2026, 9, 30, 12, 0, tzinfo=UTC),
    )
    replay_session.play(
        now=datetime(2026, 9, 30, 12, 1, tzinfo=UTC),
    )

    prefetcher = MagicMock()
    page = ReplayObservationPage(
        observations=[],
        next_cursor=None,
    )
    prefetcher.fetch_next.return_value = page

    coordinator = ReplayStreamCoordinator(
        prefetcher=prefetcher,
    )

    result = coordinator.advance(
        replay_session,
        elapsed=timedelta(seconds=30),
        now=datetime(2026, 9, 30, 12, 1, 30, tzinfo=UTC),
    )

    assert result == page
    assert replay_session.position == replay_session.end_time
    assert replay_session.state.value == "completed"

    prefetcher.fetch_next.assert_called_once_with(
        start_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        end_time=replay_session.end_time,
    )
def test_advance_fetches_all_pages_in_window() -> None:
    replay_session = ReplaySession.create(
        session_id="test-session",
        start_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 11, 0, tzinfo=UTC),
        now=datetime(2026, 9, 30, 12, 0, tzinfo=UTC),
    )
    replay_session.play(
        now=datetime(2026, 9, 30, 12, 1, tzinfo=UTC),
    )

    cursor = ReplayCursor(
        observed_at=datetime(2026, 9, 1, 10, 0, 5, tzinfo=UTC),
        observation_id=42,
    )

    first_observation = MagicMock()
    second_observation = MagicMock()

    first_page = ReplayObservationPage(
        observations=[first_observation],
        next_cursor=cursor,
    )
    second_page = ReplayObservationPage(
        observations=[second_observation],
        next_cursor=None,
    )

    prefetcher = MagicMock()
    prefetcher.fetch_next.side_effect = [
        first_page,
        second_page,
    ]

    coordinator = ReplayStreamCoordinator(
        prefetcher=prefetcher,
    )

    result = coordinator.advance(
        replay_session,
        elapsed=timedelta(seconds=10),
        now=datetime(2026, 9, 30, 12, 1, 10, tzinfo=UTC),
    )

    assert result.observations == [
        first_observation,
        second_observation,
    ]
    assert result.next_cursor is None

    prefetcher.fetch_next.assert_any_call(
        start_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 10, 0, 10, tzinfo=UTC),
    )
    prefetcher.fetch_next.assert_any_call(
        start_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 10, 0, 10, tzinfo=UTC),
        cursor=cursor,
    )
    assert prefetcher.fetch_next.call_count == 2

def test_seek_clears_prefetched_observations() -> None:
    prefetcher = MagicMock()

    coordinator = ReplayStreamCoordinator(
        prefetcher=prefetcher,
    )

    coordinator.handle_seek()

    prefetcher.clear.assert_called_once_with()

def test_fetch_window_retrieves_observations_without_advancing_session() -> None:
    start_time = datetime(2026, 9, 1, 10, 0, tzinfo=UTC)
    end_time = datetime(2026, 9, 1, 10, 0, 10, tzinfo=UTC)

    observation = MagicMock()
    page = ReplayObservationPage(
        observations=[observation],
        next_cursor=None,
    )

    prefetcher = MagicMock()
    prefetcher.fetch_next.return_value = page

    coordinator = ReplayStreamCoordinator(
        prefetcher=prefetcher,
    )

    result = coordinator.fetch_window(
        start_time=start_time,
        end_time=end_time,
    )

    assert result == page
    prefetcher.fetch_next.assert_called_once_with(
        start_time=start_time,
        end_time=end_time,
    )
