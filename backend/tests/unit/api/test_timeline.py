from datetime import UTC, datetime
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.api.routes.timeline import get_timeline_service
from app.main import create_app
from app.timeline.models import HistoryBounds, TimelineResponse
from app.timeline.service import TimelineError, TimelineService


def test_timeline_route_and_openapi() -> None:
    app = create_app()
    service = Mock(spec=TimelineService)
    service.timeline.return_value = TimelineResponse(
        generated_at=datetime.now(UTC),
        history=HistoryBounds(start_time=None, end_time=None),
        start_time=None,
        end_time=None,
        source_resolution=None,
        bucket_seconds=None,
        density_coverage=None,
        aggregation_status="not_applicable",
    )
    app.dependency_overrides[get_timeline_service] = lambda: service
    client = TestClient(app)
    try:
        response = client.get("/api/v1/timeline")
        assert response.status_code == 200
        assert response.json()["buckets"] == []
        assert "/api/v1/timeline" in client.get("/openapi.json").json()["paths"]
    finally:
        client.close()


@pytest.mark.parametrize(
    "query", ["max_buckets=0", "event_limit=501", "resolution=year", "start_time=oops"]
)
def test_query_validation(query: str) -> None:
    app = create_app()
    app.dependency_overrides[get_timeline_service] = lambda: Mock(spec=TimelineService)
    client = TestClient(app)
    assert client.get(f"/api/v1/timeline?{query}").status_code == 422
    client.close()


@pytest.mark.parametrize(
    "message,status",
    [
        ("start_time must be before end_time", 400),
        ("Invalid or stale event cursor; refresh the timeline", 409),
    ],
)
def test_domain_error_mapping(message: str, status: int) -> None:
    app = create_app()
    service = Mock(spec=TimelineService)
    service.timeline.side_effect = TimelineError(message, status)
    app.dependency_overrides[get_timeline_service] = lambda: service
    client = TestClient(app)
    response = client.get("/api/v1/timeline")
    assert response.status_code == status
    assert "error" in response.json()
    client.close()
