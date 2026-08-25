from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

from app.health import (
    HealthStatus,
    noaa_health,
    psk_reporter_health,
)

router = APIRouter(
    prefix="/health",
    tags=["health"],
)


class ProviderHealthResponse(BaseModel):
    provider: str
    status: HealthStatus
    last_success_at: datetime | None
    last_failure_at: datetime | None
    last_error: str | None


class ApplicationHealthResponse(BaseModel):
    status: HealthStatus
    providers: list[ProviderHealthResponse]


def _provider_response(
    health: object,
) -> ProviderHealthResponse:
    return ProviderHealthResponse.model_validate(
        health,
        from_attributes=True,
    )


@router.get(
    "",
    response_model=ApplicationHealthResponse,
)
def get_health() -> ApplicationHealthResponse:
    providers = [
        _provider_response(noaa_health),
        _provider_response(psk_reporter_health),
    ]

    if any(provider.status is HealthStatus.UNHEALTHY for provider in providers):
        status = HealthStatus.UNHEALTHY

    elif all(provider.status is HealthStatus.HEALTHY for provider in providers):
        status = HealthStatus.HEALTHY

    else:
        status = HealthStatus.UNKNOWN

    return ApplicationHealthResponse(
        status=status,
        providers=providers,
    )


@router.get(
    "/noaa",
    response_model=ProviderHealthResponse,
)
def get_noaa_health() -> ProviderHealthResponse:
    return _provider_response(noaa_health)


@router.get(
    "/psk-reporter",
    response_model=ProviderHealthResponse,
)
def get_psk_reporter_health() -> ProviderHealthResponse:
    return _provider_response(psk_reporter_health)
