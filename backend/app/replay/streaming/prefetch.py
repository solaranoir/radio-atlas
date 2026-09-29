from datetime import datetime

from app.replay.streaming.models import ReplayCursor, ReplayObservationPage
from app.replay.streaming.source import ReplayObservationSource


class ReplayObservationPrefetcher:
    def __init__(
        self,
        *,
        source: ReplayObservationSource,
        page_size: int = 100,
    ) -> None:
        self._source = source
        self._page_size = page_size
        self.buffered_page: ReplayObservationPage | None = None
        self._buffered_start_time: datetime | None = None
        self._buffered_end_time: datetime | None = None
        self._buffered_cursor: ReplayCursor | None = None

    def fetch_next(
        self,
        *,
        start_time: datetime,
        end_time: datetime,
        cursor: ReplayCursor | None = None,
    ) -> ReplayObservationPage:
        buffer_matches_request = (
            self.buffered_page is not None
            and self._buffered_start_time == start_time
            and self._buffered_end_time == end_time
            and self._buffered_cursor == cursor
        )

        if buffer_matches_request:
            assert self.buffered_page is not None
            page = self.buffered_page
        else:
            page = self._source.fetch_page(
                start_time=start_time,
                end_time=end_time,
                limit=self._page_size,
                cursor_time=cursor.observed_at if cursor is not None else None,
                cursor_id=cursor.observation_id if cursor is not None else None,
            )

        self.buffered_page = None
        self._buffered_start_time = None
        self._buffered_end_time = None
        self._buffered_cursor = None

        if page.next_cursor is not None:
            self.buffered_page = self._source.fetch_page(
                start_time=start_time,
                end_time=end_time,
                limit=self._page_size,
                cursor_time=page.next_cursor.observed_at,
                cursor_id=page.next_cursor.observation_id,
            )
            self._buffered_start_time = start_time
            self._buffered_end_time = end_time
            self._buffered_cursor = page.next_cursor

        return page
