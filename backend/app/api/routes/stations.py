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
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "validation_error",
                            "message": "Request validation failed",
                            "details": [
                                {
                                    "type": "greater_than_equal",
                                    "loc": ["query", "limit"],
                                    "msg": ("Input should be greater than or equal to 1"),
                                }
                            ],
                        }
                    }
                }
            },
        },
        500: {
            "description": "Response validation error",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "response_validation_error",
                            "message": "Response validation failed",
                        }
                    }
                }
            },
        },
    },
)
def get_stations(
    session: Annotated[
        Session,
        Depends(get_db),
    ],
    callsign: Annotated[
        str | None,
        Query(
            description=(
                "Filter stations by amateur-radio callsign. "
                "Callsign matching is case-insensitive and is normalized "
                "to uppercase for querying."
            ),
            examples=["KK7QEA"],
        ),
    ] = None,
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=500,
            description=("Maximum number of stations to return. Must be between 1 and 500."),
            examples=[100],
        ),
    ] = 100,
    offset: Annotated[
        int,
        Query(
            ge=0,
            description=(
                "Number of stations to skip before returning results. "
                "Use with limit for pagination."
            ),
            examples=[0],
        ),
    ] = 0,
) -> list[Station]:
    return list_stations(
        session,
        callsign=callsign,
        limit=limit,
        offset=offset,
    )
