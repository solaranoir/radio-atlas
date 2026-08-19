from __future__ import annotations

import asyncio
from time import perf_counter
from typing import Any

import httpx

from app.logging.logger import get_logger

logger = get_logger(__name__)

RETRYABLE_STATUS_CODES = {
    429,
    500,
    502,
    503,
    504,
}


class HttpClientError(RuntimeError):
    """Base exception raised by the application HTTP client."""


class HttpResponseError(HttpClientError):
    """Raised when a server returns an unsuccessful HTTP response."""


class HttpJsonDecodeError(HttpClientError):
    """Raised when an HTTP response does not contain valid JSON."""


class JsonHttpClient:
    """Reusable asynchronous HTTP client for JSON APIs."""

    def __init__(
        self,
        *,
        client: httpx.AsyncClient | None = None,
        timeout_seconds: float = 10.0,
        max_attempts: int = 3,
        backoff_seconds: float = 0.5,
    ) -> None:
        self._client = client or httpx.AsyncClient()
        self._owns_client = client is None
        self._timeout_seconds = timeout_seconds
        self._max_attempts = max_attempts
        self._backoff_seconds = backoff_seconds

    async def get_json(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> Any:
        for attempt in range(1, self._max_attempts + 1):
            started_at = perf_counter()

            try:
                response = await self._client.get(
                    url,
                    params=params,
                    timeout=self._timeout_seconds,
                )

                duration_ms = round(
                    (perf_counter() - started_at) * 1000,
                    2,
                )

                logger.info(
                    "HTTP request completed",
                    extra={
                        "operation": "http_get",
                        "url": url,
                        "status_code": response.status_code,
                        "duration_ms": duration_ms,
                        "attempt": attempt,
                    },
                )

                if response.status_code in RETRYABLE_STATUS_CODES:
                    raise httpx.HTTPStatusError(
                        "Retryable HTTP response",
                        request=response.request,
                        response=response,
                    )

                response.raise_for_status()

                try:
                    return response.json()
                except ValueError as exc:
                    raise HttpJsonDecodeError(f"Response from {url} was not valid JSON") from exc
            except httpx.TimeoutException as exc:
                logger.warning(
                    "HTTP request timed out",
                    extra={
                        "operation": "http_get",
                        "url": url,
                        "attempt": attempt,
                        "max_attempts": self._max_attempts,
                    },
                )

                if attempt == self._max_attempts:
                    raise HttpClientError(
                        f"Request to {url} timed out after {self._max_attempts} attempts"
                    ) from exc

            except httpx.TransportError as exc:
                logger.warning(
                    "HTTP transport error",
                    extra={
                        "operation": "http_get",
                        "url": url,
                        "attempt": attempt,
                        "max_attempts": self._max_attempts,
                        "error": str(exc),
                    },
                )

                if attempt == self._max_attempts:
                    raise HttpClientError(
                        f"Request to {url} failed after {self._max_attempts} attempts"
                    ) from exc

            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code

                retryable = status_code in RETRYABLE_STATUS_CODES

                logger.warning(
                    "HTTP response error",
                    extra={
                        "operation": "http_get",
                        "url": url,
                        "status_code": status_code,
                        "attempt": attempt,
                        "max_attempts": self._max_attempts,
                        "retryable": retryable,
                    },
                )

                if not retryable or attempt == self._max_attempts:
                    raise HttpResponseError(
                        f"Request to {url} returned HTTP {status_code}"
                    ) from exc
            delay = self._backoff_seconds * (2 ** (attempt - 1))

            logger.info(
                "Retrying HTTP request",
                extra={
                    "operation": "http_retry",
                    "url": url,
                    "attempt": attempt,
                    "next_attempt": attempt + 1,
                    "delay_seconds": delay,
                },
            )

            await asyncio.sleep(delay)

        raise HttpClientError(f"Request to {url} failed unexpectedly")

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> JsonHttpClient:
        return self

    async def __aexit__(
        self,
        exc_type: object,
        exc: BaseException | None,
        traceback: object,
    ) -> None:
        await self.aclose()
