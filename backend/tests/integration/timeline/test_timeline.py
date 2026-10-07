from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.analytics.aggregation.jobs import run_daily_aggregation, run_hourly_aggregation
from app.api.dependencies import get_db
from app.infrastructure.database.models import Provider, Spot
from app.main import create_app
from app.timeline.service import TimelineService
from app.timeline.source import TimelineSource

pytestmark = pytest.mark.integration
START = datetime(1998, 1, 1, tzinfo=UTC)


@pytest.mark.parametrize("resolution", ["minute", "hour", "day"])
def test_seeded_timeline_counts_exact_boundaries(db_session: Session, resolution: str) -> None:
    provider = Provider(
        name=f"timeline-{uuid4()}", display_name="Timeline fixture", provider_type="spot"
    )
    db_session.add(provider)
    db_session.flush()
    for index, (minutes, band) in enumerate(
        [(0, "20m"), (15, "20m"), (60, "40m"), (90, None), (120, "20m")]
    ):
        db_session.add(
            Spot(
                provider_id=provider.id,
                sequence_number=index,
                sender_callsign="TEST",
                receiver_callsign="FIXTURE",
                mode="FT8",
                band=band,
                observed_at=START + timedelta(minutes=minutes),
            )
        )
    db_session.flush()
    for hour in range(3):
        run_hourly_aggregation(db_session, bucket_start=START + timedelta(hours=hour))
    run_daily_aggregation(db_session, bucket_start=START)
    result = TimelineService(TimelineSource(db_session)).timeline(
        start_time=START + timedelta(minutes=15),
        end_time=START + timedelta(hours=2),
        max_buckets=1,
        resolution=resolution,  # type: ignore[arg-type]
    )
    assert sum(bucket.observation_count for bucket in result.buckets) == (
        3 if resolution == "minute" else 2
    )
    assert result.buckets[0].start_time == START + timedelta(minutes=15)
    assert result.buckets[-1].end_time == START + timedelta(hours=2)


def test_http_timeline_uses_real_queries(db_session: Session) -> None:
    app = create_app()
    app.dependency_overrides[get_db] = lambda: db_session
    client = TestClient(app)
    try:
        response = client.get(
            "/api/v1/timeline",
            params={
                "start_time": START.isoformat(),
                "end_time": (START + timedelta(minutes=1)).isoformat(),
            },
        )
        assert response.status_code == 200, response.text
        assert response.json()["buckets"][0]["observation_count"] == 0
    finally:
        client.close()
