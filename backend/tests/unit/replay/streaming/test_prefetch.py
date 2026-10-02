from datetime import UTC, datetime
from unittest.mock import MagicMock

from app.infrastructure.database.models import Spot
from app.replay.streaming.models import ReplayCursor, ReplayObservationPage
from app.replay.streaming.prefetch import ReplayObservationPrefetcher


def test_prefetcher_fetches_next_page_using_cursor() -> None:
    source = MagicMock()

    first = MagicMock(spec=Spot)
    first.observed_at = datetime(2026, 9, 1, 12, 10, tzinfo=UTC)
    first.id = 41

    cursor = ReplayCursor(
        observed_at=first.observed_at,
        observation_id=first.id,
    )

    source.fetch_page.return_value = ReplayObservationPage(
        observations=[first],
        next_cursor=None,
    )

    prefetcher = ReplayObservationPrefetcher(
        source=source,
        page_size=100,
    )

    page = prefetcher.fetch_next(
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 13, 0, tzinfo=UTC),
        cursor=cursor,
    )

    assert page.observations == [first]

    source.fetch_page.assert_called_once_with(
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 13, 0, tzinfo=UTC),
        limit=100,
        cursor_time=cursor.observed_at,
        cursor_id=cursor.observation_id,
    )


def test_prefetcher_buffers_next_page() -> None:
    source = MagicMock()

    first = MagicMock(spec=Spot)
    first.observed_at = datetime(2026, 9, 1, 12, 10, tzinfo=UTC)
    first.id = 41

    second = MagicMock(spec=Spot)
    second.observed_at = datetime(2026, 9, 1, 12, 20, tzinfo=UTC)
    second.id = 42

    cursor = ReplayCursor(
        observed_at=first.observed_at,
        observation_id=first.id,
    )

    first_page = ReplayObservationPage(
        observations=[first],
        next_cursor=cursor,
    )
    second_page = ReplayObservationPage(
        observations=[second],
        next_cursor=None,
    )

    source.fetch_page.side_effect = [
        first_page,
        second_page,
    ]

    prefetcher = ReplayObservationPrefetcher(
        source=source,
        page_size=100,
    )

    page = prefetcher.fetch_next(
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 13, 0, tzinfo=UTC),
    )

    assert page == first_page
    assert prefetcher.buffered_page == second_page
    assert source.fetch_page.call_count == 2


def test_prefetcher_returns_buffered_page_without_refetching_it() -> None:
    source = MagicMock()

    first = MagicMock(spec=Spot)
    first.observed_at = datetime(2026, 9, 1, 12, 10, tzinfo=UTC)
    first.id = 41

    second = MagicMock(spec=Spot)
    second.observed_at = datetime(2026, 9, 1, 12, 20, tzinfo=UTC)
    second.id = 42

    cursor = ReplayCursor(
        observed_at=first.observed_at,
        observation_id=first.id,
    )

    first_page = ReplayObservationPage(
        observations=[first],
        next_cursor=cursor,
    )
    second_page = ReplayObservationPage(
        observations=[second],
        next_cursor=None,
    )

    source.fetch_page.side_effect = [
        first_page,
        second_page,
    ]

    prefetcher = ReplayObservationPrefetcher(
        source=source,
        page_size=100,
    )

    returned_first = prefetcher.fetch_next(
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 13, 0, tzinfo=UTC),
    )

    returned_second = prefetcher.fetch_next(
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 13, 0, tzinfo=UTC),
        cursor=cursor,
    )

    assert returned_first == first_page
    assert returned_second == second_page
    assert source.fetch_page.call_count == 2


def test_prefetcher_does_not_use_buffer_after_window_changes() -> None:
    source = MagicMock()

    first_page = ReplayObservationPage(
        observations=[],
        next_cursor=ReplayCursor(
            observed_at=datetime(2026, 9, 1, 12, 30, tzinfo=UTC),
            observation_id=42,
        ),
    )
    buffered_page = ReplayObservationPage(
        observations=[],
        next_cursor=None,
    )
    new_window_page = ReplayObservationPage(
        observations=[],
        next_cursor=None,
    )

    source.fetch_page.side_effect = [
        first_page,
        buffered_page,
        new_window_page,
    ]

    prefetcher = ReplayObservationPrefetcher(
        source=source,
        page_size=100,
    )

    prefetcher.fetch_next(
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 13, 0, tzinfo=UTC),
    )

    returned_page = prefetcher.fetch_next(
        start_time=datetime(2026, 9, 1, 14, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 15, 0, tzinfo=UTC),
    )

    assert returned_page == new_window_page
    assert source.fetch_page.call_count == 3


def test_prefetcher_does_not_use_buffer_after_cursor_changes() -> None:
    source = MagicMock()

    first_cursor = ReplayCursor(
        observed_at=datetime(2026, 9, 1, 12, 20, tzinfo=UTC),
        observation_id=42,
    )
    seek_cursor = ReplayCursor(
        observed_at=datetime(2026, 9, 1, 12, 45, tzinfo=UTC),
        observation_id=99,
    )

    first_page = ReplayObservationPage(
        observations=[],
        next_cursor=first_cursor,
    )
    buffered_page = ReplayObservationPage(
        observations=[],
        next_cursor=None,
    )
    seek_page = ReplayObservationPage(
        observations=[],
        next_cursor=None,
    )

    source.fetch_page.side_effect = [
        first_page,
        buffered_page,
        seek_page,
    ]

    prefetcher = ReplayObservationPrefetcher(
        source=source,
        page_size=100,
    )

    prefetcher.fetch_next(
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 13, 0, tzinfo=UTC),
    )

    returned_page = prefetcher.fetch_next(
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 13, 0, tzinfo=UTC),
        cursor=seek_cursor,
    )

    assert returned_page == seek_page
    assert source.fetch_page.call_count == 3

def test_prefetcher_clear_discards_buffered_page() -> None:
    source = MagicMock()

    cursor = ReplayCursor(
        observed_at=datetime(2026, 9, 1, 12, 30, tzinfo=UTC),
        observation_id=42,
    )

    first_page = ReplayObservationPage(
        observations=[],
        next_cursor=cursor,
    )
    buffered_page = ReplayObservationPage(
        observations=[],
        next_cursor=None,
    )

    source.fetch_page.side_effect = [
        first_page,
        buffered_page,
    ]

    prefetcher = ReplayObservationPrefetcher(
        source=source,
        page_size=100,
    )

    prefetcher.fetch_next(
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 13, 0, tzinfo=UTC),
    )

    assert prefetcher.buffered_page == buffered_page

    prefetcher.clear()

    assert prefetcher.buffered_page is None
