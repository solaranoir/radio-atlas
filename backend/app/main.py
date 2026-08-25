# backend/app/main.py

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
from app.logging.logger import configure_logging


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title="SolaraSphere: Radio Atlas API",
        version="0.1.0",
    )

    app.include_router(api_router)

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

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
