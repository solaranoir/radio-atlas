from datetime import datetime

from sqlalchemy.orm import Session

from app.replay.streaming.models import (
    ReplayActivityBucket,
    ReplayCursor,
    ReplayObservationPage,
)
from app.replay.streaming.queries import (
    build_replay_activity_query,
    build_replay_observations_query,
)


class ReplayObservationSource:
    def __init__(self, session: Session) -> None:
        self._session = session

    def fetch_page(
        self,
        *,
        start_time: datetime,
        end_time: datetime,
        limit: int = 100,
        cursor_time: datetime | None = None,
        cursor_id: int | None = None,
    ) -> ReplayObservationPage:
        if limit <= 0:
            raise ValueError("limit must be greater than zero")

        query = build_replay_observations_query(
            start_time=start_time,
            end_time=end_time,
            limit=limit + 1,
            cursor_time=cursor_time,
            cursor_id=cursor_id,
        )

        results = list(self._session.scalars(query).all())

        has_more = len(results) > limit
        observations = results[:limit]
        next_cursor = None

        if has_more and observations:
            last_observation = observations[-1]
            next_cursor = ReplayCursor(
                observed_at=last_observation.observed_at,
                observation_id=last_observation.id,
            )

        return ReplayObservationPage(
            observations=observations,
            next_cursor=next_cursor,
        )

    def fetch_activity_buckets(
        self,
        *,
        start_time: datetime,
        end_time: datetime,
    ) -> list[ReplayActivityBucket]:
        query = build_replay_activity_query(
            start_time=start_time,
            end_time=end_time,
        )

        rows = self._session.execute(query).all()

        return [
            ReplayActivityBucket(
                bucket_start=bucket_start,
                observation_count=observation_count,
            )
            for bucket_start, observation_count in rows
        ]
