from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.infrastructure.database.models import Station
from app.repositories.stations import list_stations

router = APIRouter(
    prefix="/stations",
    tags=["stations"],
)


class StationResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 42,
                "callsign": "KK7QEA",
                "grid_square": "DM25",
                "latitude": 36.0395,
                "longitude": -114.9817,
                "entity_id": 291,
                "first_seen_at": "2026-08-20T12:00:00Z",
                "last_seen_at": "2026-08-24T17:30:00Z",
            }
        },
    )

    id: int
    callsign: str
    grid_square: str | None
    latitude: float | None
    longitude: float | None
    entity_id: int | None
    first_seen_at: datetime | None
    last_seen_at: datetime | None


@router.get(
    "",
    response_model=list[StationResponse],
    summary="List amateur radio stations",
    description=(
        "Returns amateur radio stations observed by Radio Atlas. "
        "Results are ordered by callsign ascending and may be filtered "
        "by callsign."
    ),
    responses={
        422: {
            "description": "Request validation error",
        },
        500: {
            "description": "Response validation error",
        },
    },
)
def get_stations(
    session: Annotated[
        Session,
        Depends(get_db),
    ],
    callsign: str | None = None,
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> list[Station]:
    stations = list_stations(
        session,
        callsign=callsign,
        limit=limit,
        offset=offset,
    )

    return stations
