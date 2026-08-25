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
        },
        422: {
            "description": "Request validation error",
        },
        500: {
            "description": "Response validation error",
        },
    },
)
def get_observations(
    session: Annotated[
        Session,
        Depends(get_db),
    ],
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    band: str | None = None,
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> list[Spot]:
    validate_time_range(
        start_time,
        end_time,
    )
    observations = list_observations(
        session,
        start_time=start_time,
        end_time=end_time,
        band=band,
        limit=limit,
        offset=offset,
    )

    return observations
