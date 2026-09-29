from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.infrastructure.database.models import Spot
from app.replay.streaming.models import ReplayActivityBucket
from app.replay.streaming.source import ReplayObservationSource


def test_fetch_page_returns_observations_and_next_cursor() -> None:
    session = MagicMock()

    first = MagicMock(spec=Spot)
    first.observed_at = datetime(2026, 9, 1, 12, 10, tzinfo=UTC)
    first.id = 41

    second = MagicMock(spec=Spot)
    second.observed_at = datetime(2026, 9, 1, 12, 20, tzinfo=UTC)
    second.id = 42

    third = MagicMock(spec=Spot)
    third.observed_at = datetime(2026, 9, 1, 12, 30, tzinfo=UTC)
    third.id = 43

    session.scalars.return_value.all.return_value = [
        first,
        second,
        third,
    ]

    source = ReplayObservationSource(session)

    page = source.fetch_page(
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 13, 0, tzinfo=UTC),
        limit=2,
    )

    assert page.observations == [first, second]
    assert page.next_cursor is not None
    assert page.next_cursor.observed_at == second.observed_at
    assert page.next_cursor.observation_id == second.id


def test_fetch_page_forwards_keyset_cursor() -> None:
    session = MagicMock()
    session.scalars.return_value.all.return_value = []

    source = ReplayObservationSource(session)

    cursor_time = datetime(
        2026,
        9,
        1,
        12,
        30,
        tzinfo=UTC,
    )

    source.fetch_page(
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 13, 0, tzinfo=UTC),
        limit=100,
        cursor_time=cursor_time,
        cursor_id=42,
    )


def test_fetch_page_has_no_next_cursor_when_page_is_not_full() -> None:
    session = MagicMock()

    observation = MagicMock(spec=Spot)
    observation.observed_at = datetime(
        2026,
        9,
        1,
        12,
        10,
        tzinfo=UTC,
    )
    observation.id = 41

    session.scalars.return_value.all.return_value = [
        observation,
    ]

    source = ReplayObservationSource(session)

    page = source.fetch_page(
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 13, 0, tzinfo=UTC),
        limit=2,
    )

    assert page.observations == [observation]
    assert page.next_cursor is None


@pytest.mark.parametrize("limit", [0, -1])
def test_fetch_page_rejects_non_positive_limit(limit: int) -> None:
    session = MagicMock()
    source = ReplayObservationSource(session)

    with pytest.raises(ValueError, match="limit must be greater than zero"):
        source.fetch_page(
            start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
            end_time=datetime(2026, 9, 1, 13, 0, tzinfo=UTC),
            limit=limit,
        )


def test_fetch_activity_buckets_returns_rollup_activity() -> None:
    session = MagicMock()

    bucket_start = datetime(
        2026,
        9,
        1,
        12,
        0,
        tzinfo=UTC,
    )

    session.execute.return_value.all.return_value = [
        (bucket_start, 250),
    ]

    source = ReplayObservationSource(session)

    buckets = source.fetch_activity_buckets(
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 15, 0, tzinfo=UTC),
    )

    assert buckets == [
        ReplayActivityBucket(
            bucket_start=bucket_start,
            observation_count=250,
        )
    ]
    session.execute.assert_called_once()
