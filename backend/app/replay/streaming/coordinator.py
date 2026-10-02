from datetime import datetime, timedelta

from app.replay.session.models import ReplaySession
from app.replay.streaming.models import ReplayObservationPage
from app.replay.streaming.prefetch import ReplayObservationPrefetcher


class ReplayStreamCoordinator:
    def __init__(
        self,
        *,
        prefetcher: ReplayObservationPrefetcher,
    ) -> None:
        self._prefetcher = prefetcher

    def advance(
        self,
        replay_session: ReplaySession,
        *,
        elapsed: timedelta,
        now: datetime,
    ) -> ReplayObservationPage:
        window_start = replay_session.position

        replay_session.advance(
            elapsed,
            now=now,
        )

        window_end = replay_session.position

        if window_end == window_start:
            return ReplayObservationPage(
                observations=[],
                next_cursor=None,
            )

        return self.fetch_window(
            start_time=window_start,
            end_time=window_end,
        )

    def handle_seek(self) -> None:
        self._prefetcher.clear()

    def fetch_window(
        self,
        *,
        start_time: datetime,
        end_time: datetime,
    ) -> ReplayObservationPage:
        page = self._prefetcher.fetch_next(
            start_time=start_time,
            end_time=end_time,
        )

        observations = list(page.observations)
        cursor = page.next_cursor

        while cursor is not None:
            page = self._prefetcher.fetch_next(
                start_time=start_time,
                end_time=end_time,
                cursor=cursor,
            )
            observations.extend(page.observations)
            cursor = page.next_cursor

        return ReplayObservationPage(
            observations=observations,
            next_cursor=None,
            )

