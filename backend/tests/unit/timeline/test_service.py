from datetime import UTC, datetime, timedelta
from unittest.mock import Mock

import pytest

from app.timeline.models import MAX_SAFE_COUNT, TimelineBucket
from app.timeline.service import (
    TimelineError,
    TimelineService,
    activity_events,
    marker_page,
    plan_buckets,
)
from app.timeline.source import TimelineSource

START = datetime(2026, 1, 1, tzinfo=UTC)


@pytest.mark.parametrize("days,limit,expected", [(36525, 512, 508), (1, 1, 1), (1, 24, 24)])
def test_adaptive_plan_covers_full_range(days: int, limit: int, expected: int) -> None:
    end = START + timedelta(days=days)
    _, _, intervals = plan_buckets(START, end, limit, "auto")
    assert len(intervals) == expected
    assert intervals[0][0] == START and intervals[-1][1] == end
    assert all(left[1] == right[0] for left, right in zip(intervals, intervals[1:], strict=False))


@pytest.mark.parametrize(
    "delta,selected",
    [
        (timedelta(minutes=2), "minute"),
        (timedelta(minutes=2, microseconds=1), "hour"),
        (timedelta(hours=2, microseconds=1), "day"),
    ],
)
def test_resolution_thresholds(delta: timedelta, selected: str) -> None:
    resolution, _, intervals = plan_buckets(START, START + delta, 2, "auto")
    assert resolution == selected
    assert 1 <= len(intervals) <= 2


def make_service(counts: list[int], empty: bool = False) -> TimelineService:
    source = Mock(spec=TimelineSource)
    source.history_bounds.return_value = (
        (None, None) if empty else (START, START + timedelta(hours=5))
    )
    source.counts.return_value = counts
    return TimelineService(source)


def test_empty_history_and_explicit_empty_range() -> None:
    service = make_service([0], empty=True)
    empty = service.timeline()
    assert empty.buckets == [] and empty.start_time is None
    result = service.timeline(start_time=START, end_time=START + timedelta(minutes=1))
    assert result.buckets[0].normalized_density == 0
    assert result.events == []
    assert result.density_coverage == "all_observations"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"start_time": START},
        {"start_time": START, "end_time": START},
        {"start_time": START, "end_time": START - timedelta(seconds=1)},
        {"start_time": START.replace(tzinfo=None), "end_time": START},
        {"max_buckets": 0},
        {"event_limit": 501},
        {"include_events": False, "event_cursor": "bad"},
    ],
)
def test_invalid_requests(kwargs: dict[str, object]) -> None:
    with pytest.raises(TimelineError):
        make_service([]).timeline(**kwargs)  # type: ignore[arg-type]


def test_paging_rejects_changed_snapshot_and_range() -> None:
    service = make_service([4, 0, 4, 0])
    first = service.timeline(
        start_time=START, end_time=START + timedelta(hours=4), resolution="hour", event_limit=1
    )
    assert first.next_event_cursor and len(first.events) == 1
    second = service.timeline(
        start_time=START,
        end_time=START + timedelta(hours=4),
        resolution="hour",
        event_limit=1,
        event_cursor=first.next_event_cursor,
    )
    assert second.next_event_cursor is None
    assert second.events[0].id != first.events[0].id
    service.source.counts = Mock(return_value=[5, 0, 4, 0])  # type: ignore[method-assign]
    with pytest.raises(TimelineError, match="stale"):
        service.timeline(
            start_time=START,
            end_time=START + timedelta(hours=4),
            resolution="hour",
            event_limit=1,
            event_cursor=first.next_event_cursor,
        )


@pytest.mark.parametrize("cursor", ["!", "W10=", "e30=", "bnVsbA=="])
def test_bad_cursor(cursor: str) -> None:
    with pytest.raises(TimelineError):
        marker_page([], "snapshot", 1, cursor)


@pytest.mark.parametrize(
    "counts,peaks", [([0, 4, 0], 1), ([0, 1, 0], 0), ([4, 4, 0], 0), ([4, 0, 4, 0], 2)]
)
def test_strict_activity_peaks(counts: list[int], peaks: int) -> None:
    buckets = [
        TimelineBucket(
            start_time=START + timedelta(hours=i),
            end_time=START + timedelta(hours=i + 1),
            observation_count=value,
            normalized_density=value / max(counts),
        )
        for i, value in enumerate(counts)
    ]
    assert len(activity_events(buckets, "all_observations", 3600)) == peaks


def test_unsafe_counts_and_invalid_source_shape() -> None:
    for counts in [[MAX_SAFE_COUNT + 1], [-1], []]:
        with pytest.raises(TimelineError, match="safely"):
            make_service(counts).timeline(start_time=START, end_time=START + timedelta(minutes=1))


def test_history_exclusive_end_and_microsecond_range() -> None:
    result = make_service([3]).timeline(max_buckets=1)
    assert result.history.end_time == START + timedelta(hours=5, microseconds=1)
    assert result.buckets[-1].end_time == result.history.end_time
    assert result.buckets[0].normalized_density == 1


def test_datetime_max_does_not_overflow_final_bucket() -> None:
    end = datetime.max.replace(tzinfo=UTC)
    _, _, buckets = plan_buckets(end - timedelta(seconds=1), end, 1, "day")
    assert buckets[-1][1] == end


def test_history_max_is_rejected() -> None:
    service = make_service([])
    service.source.history_bounds = Mock(return_value=(START, datetime.max.replace(tzinfo=UTC)))  # type: ignore[method-assign]
    with pytest.raises(TimelineError, match="supported date"):
        service.timeline()
