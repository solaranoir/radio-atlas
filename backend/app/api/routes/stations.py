from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.repositories.stations import list_stations

router = APIRouter(
    prefix="/stations",
    tags=["stations"],
)


class StationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
) -> list[StationResponse]:
    stations = list_stations(
        session,
        callsign=callsign,
        limit=limit,
        offset=offset,
    )

    return [StationResponse.model_validate(station) for station in stations]
