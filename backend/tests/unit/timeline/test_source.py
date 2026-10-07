from datetime import UTC, datetime, timedelta
from unittest.mock import Mock

import pytest

from app.timeline.source import TimelineSource, boundary_intervals

START = datetime(2026, 1, 1, tzinfo=UTC)


@pytest.mark.parametrize(
    "start,end,expected",
    [
        (0, 120, []),
        (15, 120, [(15, 60)]),
        (0, 75, [(60, 75)]),
        (15, 75, [(15, 60), (60, 75)]),
        (15, 30, [(15, 30)]),
    ],
)
def test_hourly_edges_are_disjoint(start: int, end: int, expected: list[tuple[int, int]]) -> None:
    result = boundary_intervals(
        START + timedelta(minutes=start), START + timedelta(minutes=end), "hour"
    )
    assert result == [
        (START + timedelta(minutes=a), START + timedelta(minutes=b)) for a, b in expected
    ]


def test_daily_minute_and_overflow_edges() -> None:
    end = START + timedelta(days=1, hours=1)
    assert boundary_intervals(START, end, "day") == [(START + timedelta(days=1), end)]
    assert boundary_intervals(START, end, "minute") == [(START, end)]
    maximum = datetime.max.replace(tzinfo=UTC)
    assert boundary_intervals(maximum - timedelta(seconds=1), maximum, "day") == [
        (maximum - timedelta(seconds=1), maximum)
    ]


def test_counts_merge_rollup_and_raw_edges_in_two_queries() -> None:
    session = Mock()
    session.execute.side_effect = [[(0, 10)], [(0, 2), (1, 3)]]
    source = TimelineSource(session)
    intervals = [
        (START + timedelta(minutes=15), START + timedelta(hours=2, minutes=15)),
        (START + timedelta(hours=2, minutes=15), START + timedelta(hours=2, minutes=30)),
    ]
    assert source.counts(intervals, "hour") == [12, 3]
    sql = str(session.execute.call_args_list[1].args[0])
    assert "raw_ranges" in sql and "spots.band IS NOT NULL" in sql


def test_aligned_rollups_avoid_raw_query() -> None:
    session = Mock()
    session.execute.return_value = [(0, 7)]
    assert TimelineSource(session).counts([(START, START + timedelta(hours=1))], "hour") == [7]
    assert session.execute.call_count == 1


def test_minute_counts_and_history_bounds() -> None:
    session = Mock()
    session.execute.return_value = [(0, 2)]
    source = TimelineSource(session)
    assert source.counts([(START, START + timedelta(minutes=1))], "minute") == [2]
    session.execute.return_value = Mock()
    session.execute.return_value.one.return_value = (START, START)
    assert source.history_bounds() == (START, START)
