import pytest
from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.main import create_app


@pytest.mark.parametrize("scheme", ["postgres", "postgresql", "postgresql+psycopg"])
def test_render_database_url_uses_installed_driver(scheme: str) -> None:
    settings = Settings(radio_atlas_database_url=f"{scheme}://localhost/test")
    assert settings.radio_atlas_database_url == "postgresql+psycopg://localhost/test"


def test_cors_accepts_configured_frontend_and_rejects_other_origins(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("RADIO_ATLAS_CORS_ORIGINS", '["https://atlas.example.org"]')
    get_settings.cache_clear()
    try:
        client = TestClient(create_app())
        for origin, expected in [
            ("https://atlas.example.org", 200),
            ("https://other.example", 400),
        ]:
            response = client.options(
                "/health",
                headers={"Origin": origin, "Access-Control-Request-Method": "GET"},
            )
            assert response.status_code == expected
            assert response.headers.get("access-control-allow-origin") == (
                origin if expected == 200 else None
            )
        client.close()
    finally:
        get_settings.cache_clear()
