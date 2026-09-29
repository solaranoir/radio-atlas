from dataclasses import dataclass
from datetime import datetime

from app.infrastructure.database.models import Spot


@dataclass(frozen=True)
class ReplayActivityBucket:
    bucket_start: datetime
    observation_count: int


@dataclass(frozen=True)
class ReplayCursor:
    observed_at: datetime
    observation_id: int


@dataclass(frozen=True)
class ReplayObservationPage:
    observations: list[Spot]
    next_cursor: ReplayCursor | None
