from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.errors import APIError
from app.api.router import api_router
from app.main import create_app


def test_create_app_returns_fastapi_application() -> None:
    app = create_app()

    assert isinstance(app, FastAPI)


def test_health_endpoint_returns_ok() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
    }


def test_openapi_is_available() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/openapi.json")

    assert response.status_code == 200

    body = response.json()

    assert body["info"]["title"] == "SolaraSphere: Radio Atlas API"
    assert body["info"]["version"] == "0.1.0"


def test_swagger_docs_are_available() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/docs")

    assert response.status_code == 200


def test_api_router_uses_v1_prefix() -> None:
    assert api_router.prefix == "/api/v1"


def test_request_id_middleware_generates_request_id() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"]


def test_request_id_middleware_preserves_supplied_request_id() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get(
        "/health",
        headers={
            "X-Request-ID": "radio-atlas-test-request",
        },
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "radio-atlas-test-request"


def test_api_error_uses_standard_error_response() -> None:
    app = create_app()

    @app.get("/test-error")
    async def test_error() -> None:
        raise APIError(
            status_code=409,
            code="test_conflict",
            message="Test conflict",
        )

    client = TestClient(app)

    response = client.get("/test-error")

    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "code": "test_conflict",
            "message": "Test conflict",
        }
    }
