from dataclasses import dataclass
from datetime import datetime, timedelta

from app.replay.session.models import ReplayState
from app.replay.session.service import ReplaySessionService
from app.replay.streaming.coordinator import ReplayStreamCoordinator
from app.replay.streaming.models import ReplayObservationPage


@dataclass(frozen=True)
class ReplayStreamTick:
    position: datetime
    page: ReplayObservationPage


def run_replay_stream_tick(
    *,
    session_id: str,
    elapsed: timedelta,
    now: datetime,
    service: ReplaySessionService,
    coordinator: ReplayStreamCoordinator,
) -> ReplayStreamTick | None:
    replay_session = service.get_session(session_id)

    if replay_session is None:
        return None

    if replay_session.state is not ReplayState.PLAYING:
        return None

    window_start = replay_session.position

    advanced_session = service.advance_session(
        session_id,
        elapsed=elapsed,
        now=now,
    )

    if advanced_session is None:
        return None

    window_end = advanced_session.position

    if window_end == window_start:
        page = ReplayObservationPage(
            observations=[],
            next_cursor=None,
        )
    else:
        page = coordinator.fetch_window(
            start_time=window_start,
            end_time=window_end,
        )

    return ReplayStreamTick(
        position=window_end,
        page=page,
    )
