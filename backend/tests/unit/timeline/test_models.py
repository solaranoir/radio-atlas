from datetime import UTC, datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.timeline.models import MAX_SAFE_COUNT, TimelineBucket, TimelineEvent

START = datetime(2026, 1, 1, tzinfo=UTC)


def test_markers_accept_future_sources_point_events_and_normalize_utc() -> None:
    local = START.astimezone(timezone(timedelta(hours=2)))
    event = TimelineEvent(
        id="anomaly:1",
        source="anomaly_detection",
        event_type="solar_anomaly",
        severity="high",
        start_time=local,
        metadata={"score": 3, "details": [True, None]},
    )
    assert event.start_time.tzinfo is UTC
    assert event.end_time is None
    assert event.model_dump(mode="json")["start_time"].endswith("Z")


def test_independent_metadata_defaults() -> None:
    first = TimelineEvent(id="one", start_time=START)
    second = TimelineEvent(id="two", start_time=START)
    first.metadata["a"] = 1
    assert second.metadata == {}


def test_reject_unsafe_marker_data() -> None:
    with pytest.raises(ValidationError):
        TimelineEvent(id="one", start_time=START, metadata={"data": "a" * 4096})
    with pytest.raises(ValidationError):
        TimelineEvent(id="one", start_time=START, metadata={"score": float("nan")})
    with pytest.raises(ValidationError):
        TimelineEvent(id="one", start_time=START, end_time=START)
    with pytest.raises(ValidationError):
        TimelineEvent(id="one", start_time=START.replace(tzinfo=None))


def test_reject_invalid_bucket_values() -> None:
    with pytest.raises(ValidationError):
        TimelineBucket(start_time=START, end_time=START, observation_count=0, normalized_density=0)
    with pytest.raises(ValidationError):
        TimelineBucket(
            start_time=START,
            end_time=START + timedelta(hours=1),
            observation_count=MAX_SAFE_COUNT + 1,
            normalized_density=1,
        )
    with pytest.raises(ValidationError):
        TimelineBucket(
            start_time=START,
            end_time=START + timedelta(hours=1),
            observation_count=1,
            normalized_density=float("inf"),
        )
