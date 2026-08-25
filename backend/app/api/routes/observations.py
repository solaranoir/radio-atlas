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
    model_config = ConfigDict(from_attributes=True)

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
