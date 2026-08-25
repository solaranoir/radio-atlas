from datetime import datetime
from typing import Annotated, Any

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
    data: dict[str, Any]


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
def get_solar_conditions(
    session: Annotated[
        Session,
        Depends(get_db),
    ],
    observation_type: Annotated[
        str | None,
        Query(
            description=(
                "Filter solar-condition records by normalized observation type. "
                "Examples include solar_flux, kp_index, sunspot_number, aurora, "
                "magnetic_field, and solar_wind."
            ),
            examples=["solar_wind"],
        ),
    ] = None,
    start_time: Annotated[
        datetime | None,
        Query(
            description=(
                "Return solar-condition records observed at or after this UTC timestamp. "
                "Use ISO 8601 format."
            ),
            examples=["2026-08-20T00:00:00Z"],
        ),
    ] = None,
    end_time: Annotated[
        datetime | None,
        Query(
            description=(
                "Return solar-condition records observed at or before this UTC timestamp. "
                "Use ISO 8601 format."
            ),
            examples=["2026-08-21T00:00:00Z"],
        ),
    ] = None,
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=500,
            description=(
                "Maximum number of solar-condition records to return. Must be between 1 and 500."
            ),
            examples=[100],
        ),
    ] = 100,
    offset: Annotated[
        int,
        Query(
            ge=0,
            description=(
                "Number of solar-condition records to skip before returning results. "
                "Use with limit for pagination."
            ),
            examples=[0],
        ),
    ] = 0,
) -> list[SolarCondition]:
    validate_time_range(
        start_time,
        end_time,
    )

    return list_solar_conditions(
        session,
        observation_type=observation_type,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=offset,
    )
