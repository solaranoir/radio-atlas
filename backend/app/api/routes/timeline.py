from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.api.errors import APIError, APIErrorResponse
from app.timeline.models import TimelineResponse
from app.timeline.service import TimelineError, TimelineService
from app.timeline.source import TimelineSource

router = APIRouter(prefix="/timeline", tags=["timeline"])


def get_timeline_service(session: Annotated[Session, Depends(get_db)]) -> TimelineService:
    return TimelineService(TimelineSource(session))


@router.get(
    "",
    response_model=TimelineResponse,
    summary="Get historical timeline",
    description=(
        "Bounded UTC density buckets and paginated activity markers. "
        "Omit both bounds for full history."
    ),
    responses={
        400: {"model": APIErrorResponse},
        409: {"model": APIErrorResponse},
        500: {"model": APIErrorResponse},
    },
)
def get_timeline(
    service: Annotated[TimelineService, Depends(get_timeline_service)],
    start_time: Annotated[
        datetime | None, Query(description="Inclusive timezone-aware start")
    ] = None,
    end_time: Annotated[datetime | None, Query(description="Exclusive timezone-aware end")] = None,
    max_buckets: Annotated[int, Query(ge=1, le=2048)] = 512,
    resolution: Literal["auto", "minute", "hour", "day"] = "auto",
    include_events: bool = True,
    event_limit: Annotated[int, Query(ge=1, le=500)] = 100,
    event_cursor: Annotated[str | None, Query(max_length=1024)] = None,
) -> TimelineResponse:
    try:
        return service.timeline(
            start_time=start_time,
            end_time=end_time,
            max_buckets=max_buckets,
            resolution=resolution,
            include_events=include_events,
            event_limit=event_limit,
            event_cursor=event_cursor,
        )
    except TimelineError as exc:
        raise APIError(exc.status_code, exc.code, str(exc)) from exc
