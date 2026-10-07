import base64
import binascii
import hashlib
import json
from datetime import UTC, datetime, timedelta
from typing import Literal

from app.timeline.models import (
    MAX_SAFE_COUNT,
    Coverage,
    HistoryBounds,
    Resolution,
    TimelineBucket,
    TimelineEvent,
    TimelineResponse,
)
from app.timeline.source import TimelineSource


class TimelineError(ValueError):
    def __init__(
        self, message: str, status_code: int = 400, code: str = "invalid_timeline_request"
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code


def plan_buckets(
    start: datetime, end: datetime, limit: int, resolution: Literal["auto", "minute", "hour", "day"]
) -> tuple[Resolution, int, list[tuple[datetime, datetime]]]:
    delta = end - start
    duration = (delta.days * 86400 + delta.seconds) * 1_000_000 + delta.microseconds
    units: dict[Resolution, int] = {"minute": 60, "hour": 3600, "day": 86400}
    selected: Resolution = "day"
    if resolution == "auto":
        for candidate, seconds in units.items():
            if duration <= limit * seconds * 1_000_000:
                selected = candidate
                break
    else:
        selected = resolution
    unit = units[selected]
    divisor = limit * unit * 1_000_000
    width = unit * max(1, (duration + divisor - 1) // divisor)
    count = (duration + width * 1_000_000 - 1) // (width * 1_000_000)
    intervals = []
    for index in range(count):
        lower = start + timedelta(seconds=index * width)
        # Add only the remaining duration at the last bucket to avoid datetime overflow.
        upper = lower + min(timedelta(seconds=width), end - lower)
        intervals.append((lower, upper))
    return selected, width, intervals


def activity_events(
    buckets: list[TimelineBucket], coverage: Coverage, width: int
) -> list[TimelineEvent]:
    counts = [bucket.observation_count for bucket in buckets]
    ordered = sorted(counts)
    # Twice the median stays integral, avoiding rounded comparisons for large counts.
    threshold = (ordered[(len(ordered) - 1) // 2] + ordered[len(ordered) // 2]) if ordered else 0
    events = []
    for index, bucket in enumerate(buckets):
        count = bucket.observation_count
        left = counts[index - 1] if index else 0
        right = counts[index + 1] if index + 1 < len(counts) else 0
        if count > max(left, right) and count >= max(2, threshold):
            events.append(
                TimelineEvent(
                    id=f"activity:{coverage}:{width}:{bucket.start_time.isoformat()}:{bucket.end_time.isoformat()}",
                    start_time=bucket.start_time,
                    end_time=bucket.end_time,
                    observation_count=count,
                )
            )
    return events


def marker_page(
    events: list[TimelineEvent], binding: str, limit: int, cursor: str | None
) -> tuple[list[TimelineEvent], str | None]:
    offset = 0
    if cursor is not None:
        try:
            decoded = json.loads(base64.b64decode(cursor, altchars=b"-_", validate=True))
            if (
                not isinstance(decoded, dict)
                or decoded.get("binding") != binding
                or type(decoded.get("offset")) is not int
            ):
                raise ValueError
            offset = decoded["offset"]
            if offset <= 0 or offset >= len(events):
                raise ValueError
        except (ValueError, TypeError, binascii.Error, UnicodeError) as exc:
            raise TimelineError(
                "Invalid or stale event cursor; refresh the timeline", 409, "stale_event_cursor"
            ) from exc
    next_offset = offset + limit
    next_cursor = None
    if next_offset < len(events):
        next_cursor = base64.urlsafe_b64encode(
            json.dumps({"binding": binding, "offset": next_offset}, separators=(",", ":")).encode()
        ).decode()
    return events[offset:next_offset], next_cursor


class TimelineService:
    def __init__(self, source: TimelineSource) -> None:
        self.source = source

    def timeline(
        self,
        *,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        max_buckets: int = 512,
        resolution: Literal["auto", "minute", "hour", "day"] = "auto",
        include_events: bool = True,
        event_limit: int = 100,
        event_cursor: str | None = None,
    ) -> TimelineResponse:
        if not 1 <= max_buckets <= 2048 or not 1 <= event_limit <= 500:
            raise TimelineError("Timeline limits are out of range")
        if (start_time is None) != (end_time is None):
            raise TimelineError("Provide both start_time and end_time, or neither")
        if event_cursor and not include_events:
            raise TimelineError("event_cursor requires include_events")
        if start_time is not None and end_time is not None:
            if start_time.utcoffset() is None or end_time.utcoffset() is None:
                raise TimelineError("Timeline timestamps must include a timezone")
            start_time, end_time = start_time.astimezone(UTC), end_time.astimezone(UTC)
            if start_time >= end_time:
                raise TimelineError("start_time must be before end_time")
        first, last = self.source.history_bounds()
        first = first.astimezone(UTC) if first else None
        last = last.astimezone(UTC) if last else None
        try:
            history = HistoryBounds(
                start_time=first, end_time=last + timedelta(microseconds=1) if last else None
            )
        except OverflowError as exc:
            raise TimelineError("History timestamp exceeds the supported date range") from exc
        if start_time is None:
            start_time, end_time = history.start_time, history.end_time
        if start_time is None or end_time is None:
            if event_cursor:
                raise TimelineError("Event cursor has no historical range")
            return TimelineResponse(
                generated_at=datetime.now(UTC),
                history=history,
                start_time=None,
                end_time=None,
                source_resolution=None,
                bucket_seconds=None,
                density_coverage=None,
                aggregation_status="not_applicable",
            )
        selected, width, intervals = plan_buckets(start_time, end_time, max_buckets, resolution)
        counts = self.source.counts(intervals, selected)
        if len(counts) != len(intervals) or any(
            not 0 <= value <= MAX_SAFE_COUNT for value in counts
        ):
            raise TimelineError(
                "Timeline counts cannot be represented safely", 500, "invalid_timeline_data"
            )
        maximum = max(counts, default=0)
        buckets = [
            TimelineBucket(
                start_time=lower,
                end_time=upper,
                observation_count=count,
                normalized_density=count / maximum if maximum else 0,
            )
            for (lower, upper), count in zip(intervals, counts, strict=True)
        ]
        coverage: Coverage = (
            "all_observations" if selected == "minute" else "band_resolved_observations"
        )
        events = activity_events(buckets, coverage, width) if include_events else []
        # Bind cursors to the derived snapshot and all options affecting marker retrieval.
        signature = json.dumps(
            [
                start_time.isoformat(),
                end_time.isoformat(),
                selected,
                width,
                coverage,
                max_buckets,
                event_limit,
                history.model_dump(mode="json"),
                counts,
            ],
            separators=(",", ":"),
        )
        binding = hashlib.sha256(signature.encode()).hexdigest()
        page, next_cursor = marker_page(events, binding, event_limit, event_cursor)
        return TimelineResponse(
            generated_at=datetime.now(UTC),
            history=history,
            start_time=start_time,
            end_time=end_time,
            source_resolution=selected,
            bucket_seconds=width,
            density_coverage=coverage,
            aggregation_status="not_applicable" if selected == "minute" else "unknown",
            buckets=buckets,
            events=page,
            next_event_cursor=next_cursor,
        )
