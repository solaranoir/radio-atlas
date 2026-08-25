# backend/app/main.py

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.exceptions import (
    RequestValidationError,
    ResponseValidationError,
)

from app.api.errors import (
    APIError,
    api_error_handler,
    request_validation_error_handler,
    response_validation_error_handler,
)
from app.api.middleware import request_id_middleware
from app.api.router import api_router
from app.api.routes.health import router as health_router
from app.ingestion.runtime import run_ingestion_runtime
from app.logging.logger import configure_logging


@asynccontextmanager
async def lifespan(
    _app: FastAPI,
) -> AsyncIterator[None]:
    ingestion_task = asyncio.create_task(
        run_ingestion_runtime(),
        name="radio-atlas-ingestion",
    )

    try:
        yield
    finally:
        ingestion_task.cancel()

        with suppress(asyncio.CancelledError):
            await ingestion_task


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title="SolaraSphere: Radio Atlas API",
        version="0.1.0",
        description=(
            "Radio Atlas Phase 1 API for normalized amateur-radio "
            "observations, solar conditions, and station data."
        ),
        lifespan=lifespan,
    )

    app.include_router(api_router)
    app.include_router(health_router)

    app.middleware("http")(request_id_middleware)

    app.add_exception_handler(
        APIError,
        api_error_handler,
    )

    app.add_exception_handler(
        RequestValidationError,
        request_validation_error_handler,
    )

    app.add_exception_handler(
        ResponseValidationError,
        response_validation_error_handler,
    )

    return app


app = create_app()
