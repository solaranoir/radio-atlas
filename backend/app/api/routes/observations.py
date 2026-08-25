from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.api.validation import validate_time_range
from app.infrastructure.database.models import Spot
from app.repositories.observations import list_observations

router = APIRouter(
    prefix="/observations",
    tags=["observations"],
)


class ObservationResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 42,
                "provider_id": 2,
                "sequence_number": 71899472730,
                "sender_callsign": "EA5JLN",
                "receiver_callsign": "DL4JC",
                "sender_grid": "IM99TN",
                "receiver_grid": "JN39LH",
                "frequency_hz": 14_075_361,
                "band": "20m",
                "mode": "FT8",
                "snr_db": -5,
                "observed_at": "2026-08-20T20:35:44Z",
                "transmitted_at": "2026-08-20T20:35:29Z",
            }
        },
    )

    id: int
    provider_id: int
    sequence_number: int | None

    sender_callsign: str
    receiver_callsign: str

    sender_grid: str | None
    receiver_grid: str | None

    frequency_hz: int | None
    band: str | None
    mode: str

    snr_db: int | None

    observed_at: datetime
    transmitted_at: datetime | None


@router.get(
    "",
    response_model=list[ObservationResponse],
    summary="List radio observations",
    description=(
        "Returns normalized PSK Reporter spot observations. "
        "Results are ordered newest-first and may be filtered "
        "by time range and amateur-radio band."
    ),
    responses={
        400: {
            "description": "Invalid time range",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "invalid_time_range",
                            "message": ("start_time must be before or equal to end_time"),
                            "details": None,
                        }
                    }
                }
            },
        },
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
def get_observations(
    session: Annotated[
        Session,
        Depends(get_db),
    ],
    start_time: Annotated[
        datetime | None,
        Query(
            description=(
                "Return observations recorded at or after this UTC timestamp. Use ISO 8601 format."
            ),
            examples=["2026-08-20T00:00:00Z"],
        ),
    ] = None,
    end_time: Annotated[
        datetime | None,
        Query(
            description=(
                "Return observations recorded at or before this UTC timestamp. Use ISO 8601 format."
            ),
            examples=["2026-08-21T00:00:00Z"],
        ),
    ] = None,
    band: Annotated[
        str | None,
        Query(
            description=(
                "Filter observations by amateur-radio band. "
                "Band values use standard labels such as 20m, 40m, or 10m."
            ),
            examples=["20m"],
        ),
    ] = None,
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=500,
            description=("Maximum number of observations to return. Must be between 1 and 500."),
            examples=[100],
        ),
    ] = 100,
    offset: Annotated[
        int,
        Query(
            ge=0,
            description=(
                "Number of observations to skip before returning results. "
                "Use with limit for pagination."
            ),
            examples=[0],
        ),
    ] = 0,
) -> list[Spot]:
    validate_time_range(
        start_time,
        end_time,
    )

    return list_observations(
        session,
        start_time=start_time,
        end_time=end_time,
        band=band,
        limit=limit,
        offset=offset,
    )
