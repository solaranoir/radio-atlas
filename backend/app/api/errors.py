from typing import cast

from fastapi import Request
from fastapi.exceptions import (
    RequestValidationError,
    ResponseValidationError,
)
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class APIError(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message

        super().__init__(message)


class APIErrorDetail(BaseModel):
    code: str
    message: str


class APIErrorResponse(BaseModel):
    error: APIErrorDetail


class ValidationErrorDetail(APIErrorDetail):
    details: list[dict[str, object]]


class ValidationErrorResponse(BaseModel):
    error: ValidationErrorDetail


async def api_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    api_error = cast(APIError, exc)

    return JSONResponse(
        status_code=api_error.status_code,
        content={
            "error": {
                "code": api_error.code,
                "message": api_error.message,
            }
        },
    )


async def response_validation_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    if not isinstance(exc, ResponseValidationError):
        raise exc

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "response_validation_error",
                "message": "Response validation failed",
            }
        },
    )


async def request_validation_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    if not isinstance(exc, RequestValidationError):
        raise exc

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed",
                "details": exc.errors(),
            }
        },
    )
