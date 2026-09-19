from datetime import UTC, datetime

from app.analytics.aggregation.queries import (
    build_daily_band_aggregation_query,
    build_daily_station_aggregation_query,
    build_hourly_band_aggregation_query,
    build_hourly_station_aggregation_query,
)


def _build_query():
    return build_hourly_band_aggregation_query(
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 13, 0, tzinfo=UTC),
    )


def test_hourly_band_query_uses_hour_bucket() -> None:
    compiled = str(_build_query())

    assert "date_trunc" in compiled
    assert "GROUP BY" in compiled


def test_hourly_band_query_groups_by_band_and_mode() -> None:
    compiled = str(_build_query())

    assert "spots.band" in compiled
    assert "spots.mode" in compiled
    assert "GROUP BY" in compiled


def test_hourly_band_query_excludes_null_bands() -> None:
    compiled = str(_build_query())

    assert "spots.band IS NOT NULL" in compiled


def test_hourly_band_query_uses_half_open_time_window() -> None:
    query = _build_query()
    compiled = str(query)

    assert "spots.observed_at >=" in compiled
    assert "spots.observed_at <" in compiled
    assert "spots.observed_at <=" not in compiled


def test_hourly_band_query_calculates_expected_metrics() -> None:
    compiled = str(_build_query())

    assert "count(" in compiled.lower()
    assert "distinct(" in compiled.lower()
    assert "min(" in compiled.lower()
    assert "max(" in compiled.lower()
    assert "avg(" in compiled.lower()


def test_daily_band_query_uses_day_bucket() -> None:
    query = build_daily_band_aggregation_query(
        start_time=datetime(2026, 9, 1, 0, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 2, 0, 0, tzinfo=UTC),
    )

    compiled = str(
        query.compile(
            compile_kwargs={
                "literal_binds": True,
            }
        )
    )

    assert "date_trunc('day'" in compiled


def test_hourly_sender_station_query_uses_sender_identity() -> None:
    query = build_hourly_station_aggregation_query(
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 13, 0, tzinfo=UTC),
        direction="sender",
    )

    compiled = str(query)

    group_by_clause = compiled.split("GROUP BY", 1)[1].split("ORDER BY", 1)[0]

    assert "spots.sender_callsign" in group_by_clause
    assert "spots.sender_station_id" not in group_by_clause
    assert "max(spots.sender_station_id) AS station_id" in compiled
    assert "spots.sender_callsign AS callsign" in compiled
    assert "distinct(spots.receiver_callsign)" in compiled.lower()


def test_hourly_receiver_station_query_uses_receiver_identity() -> None:
    query = build_hourly_station_aggregation_query(
        start_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 13, 0, tzinfo=UTC),
        direction="receiver",
    )

    compiled = str(query)

    assert "max(spots.receiver_station_id) AS station_id" in compiled
    assert "spots.receiver_callsign AS callsign" in compiled
    assert "distinct(spots.sender_callsign)" in compiled.lower()


def test_daily_station_query_uses_day_bucket() -> None:
    query = build_daily_station_aggregation_query(
        start_time=datetime(2026, 9, 1, 0, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 2, 0, 0, tzinfo=UTC),
        direction="sender",
    )

    compiled = str(
        query.compile(
            compile_kwargs={
                "literal_binds": True,
            }
        )
    )

    assert "date_trunc('day'" in compiled
