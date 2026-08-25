from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.api.validation import validate_time_range
from app.infrastructure.database.models import SolarCondition
from app.repositories.solar_conditions import list_solar_conditions

router = APIRouter(
    prefix="/solar-conditions",
    tags=["solar-conditions"],
)


class SolarConditionResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 17,
                "provider_id": 1,
                "observation_type": "solar_wind",
                "observed_at": "2026-08-20T12:00:00Z",
                "value": 432.5,
                "unit": "km/s",
                "data": {
                    "density": 6.2,
                    "temperature": 118000,
                    "source": "ACE",
                },
            }
        },
    )

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
    summary="List solar conditions",
    description=(
        "Returns normalized NOAA solar and space-weather observations. "
        "Results are ordered newest-first and may be filtered "
        "by observation type and time range."
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
) -> list[SolarCondition]:
    validate_time_range(
        start_time,
        end_time,
    )
    conditions = list_solar_conditions(
        session,
        observation_type=observation_type,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=offset,
    )

    return conditions
