from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.analytics.statistics.cache import StatisticsCache
from app.analytics.statistics.service import StatisticsService
from app.infrastructure.cache.redis import get_redis_client
from app.infrastructure.database.session import create_session
from app.replay.session.service import ReplaySessionService
from app.replay.streaming.coordinator import ReplayStreamCoordinator
from app.replay.streaming.prefetch import ReplayObservationPrefetcher
from app.replay.streaming.source import ReplayObservationSource


def get_db() -> Generator[Session, None, None]:
    session = create_session()

    try:
        yield session
    finally:
        session.close()


def get_statistics_service(
    session: Annotated[Session, Depends(get_db)],
) -> StatisticsService:
    cache = StatisticsCache(get_redis_client())

    return StatisticsService(
        session,
        cache=cache,
    )

def get_replay_session_service(
    session: Annotated[Session, Depends(get_db)],
) -> ReplaySessionService:
    return ReplaySessionService(session)

def get_replay_stream_coordinator(
    session: Annotated[Session, Depends(get_db)],
) -> ReplayStreamCoordinator:
    source = ReplayObservationSource(session)
    prefetcher = ReplayObservationPrefetcher(source=source)

    return ReplayStreamCoordinator(
        prefetcher=prefetcher,
    )
