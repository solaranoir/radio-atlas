import httpx
import pytest

from app.services.http import (
    HttpClientError,
    HttpJsonDecodeError,
    HttpResponseError,
    JsonHttpClient,
)


@pytest.mark.asyncio
async def test_get_json_success() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"status": "ok"},
            request=request,
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=transport) as raw_client:
        client = JsonHttpClient(client=raw_client)

        payload = await client.get_json("https://example.test/data")

    assert payload == {"status": "ok"}


@pytest.mark.asyncio
async def test_get_json_invalid_json() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            content=b"not-json",
            request=request,
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=transport) as raw_client:
        client = JsonHttpClient(client=raw_client)

        with pytest.raises(HttpJsonDecodeError):
            await client.get_json("https://example.test/data")


@pytest.mark.asyncio
async def test_invalid_json_retries_then_succeeds() -> None:
    attempts = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        if attempts == 1:
            return httpx.Response(
                200,
                content=b'{"status":',
                request=request,
            )

        return httpx.Response(
            200,
            json={"status": "ok"},
            request=request,
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=transport) as raw_client:
        client = JsonHttpClient(
            client=raw_client,
            max_attempts=3,
            backoff_seconds=0,
        )

        payload = await client.get_json(
            "https://example.test/data",
        )

    assert attempts == 2
    assert payload == {"status": "ok"}


@pytest.mark.asyncio
async def test_invalid_json_raises_after_max_attempts() -> None:
    attempts = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        return httpx.Response(
            200,
            content=b'{"status":',
            request=request,
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=transport) as raw_client:
        client = JsonHttpClient(
            client=raw_client,
            max_attempts=3,
            backoff_seconds=0,
        )

        with pytest.raises(HttpJsonDecodeError):
            await client.get_json(
                "https://example.test/data",
            )

    assert attempts == 3


@pytest.mark.asyncio
async def test_non_retryable_400_fails_immediately() -> None:
    attempts = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        return httpx.Response(
            400,
            request=request,
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=transport) as raw_client:
        client = JsonHttpClient(
            client=raw_client,
            max_attempts=3,
            backoff_seconds=0,
        )

        with pytest.raises(HttpResponseError):
            await client.get_json("https://example.test/data")

    assert attempts == 1


@pytest.mark.asyncio
async def test_retryable_500_retries_then_succeeds() -> None:
    attempts = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        if attempts < 3:
            return httpx.Response(
                500,
                request=request,
            )

        return httpx.Response(
            200,
            json={"status": "ok"},
            request=request,
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=transport) as raw_client:
        client = JsonHttpClient(
            client=raw_client,
            max_attempts=3,
            backoff_seconds=0,
        )

        payload = await client.get_json("https://example.test/data")

    assert attempts == 3
    assert payload == {"status": "ok"}


@pytest.mark.asyncio
async def test_429_retries() -> None:
    attempts = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        if attempts == 1:
            return httpx.Response(
                429,
                request=request,
            )

        return httpx.Response(
            200,
            json={"status": "ok"},
            request=request,
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=transport) as raw_client:
        client = JsonHttpClient(
            client=raw_client,
            max_attempts=2,
            backoff_seconds=0,
        )

        payload = await client.get_json("https://example.test/data")

    assert attempts == 2
    assert payload == {"status": "ok"}


@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_timeout_retries_then_succeeds() -> None:
    attempts = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        if attempts == 1:
            raise httpx.ReadTimeout(
                "timed out",
                request=request,
            )

        return httpx.Response(
            200,
            json={"status": "ok"},
            request=request,
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=transport) as raw_client:
        client = JsonHttpClient(
            client=raw_client,
            max_attempts=2,
            backoff_seconds=0,
        )

        payload = await client.get_json("https://example.test/data")

    assert attempts == 2
    assert payload == {"status": "ok"}


@pytest.mark.asyncio
async def test_transport_error_exhaustion_raises_http_client_error() -> None:
    attempts = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        raise httpx.ConnectError(
            "connection failed",
            request=request,
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=transport) as raw_client:
        client = JsonHttpClient(
            client=raw_client,
            max_attempts=3,
            backoff_seconds=0,
        )

        with pytest.raises(HttpClientError):
            await client.get_json("https://example.test/data")

    assert attempts == 3
