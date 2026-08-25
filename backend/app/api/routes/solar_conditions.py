from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.repositories.solar_conditions import list_solar_conditions

router = APIRouter(
    prefix="/solar-conditions",
    tags=["solar-conditions"],
)


class SolarConditionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    provider_id: int
    observation_type: str
    observed_at: datetime
    value: float | None
    unit: str | None
    data: dict[str, object]


@router.get(
    "",
    response_model=list[SolarConditionResponse],
)
def get_solar_conditions(
    session: Annotated[
        Session,
        Depends(get_db),
    ],
    observation_type: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> list[SolarConditionResponse]:
    conditions = list_solar_conditions(
        session,
        observation_type=observation_type,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=offset,
    )

    return [SolarConditionResponse.model_validate(condition) for condition in conditions]
