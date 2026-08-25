from datetime import UTC, datetime
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from app.infrastructure.database.models import SolarCondition
from app.repositories.solar_conditions import (
    build_solar_conditions_query,
    list_solar_conditions,
)


def test_default_query_orders_newest_first() -> None:
    query = build_solar_conditions_query()

    compiled = str(query)

    assert "ORDER BY solar_conditions.observed_at DESC" in compiled


def test_observation_type_filter_is_applied() -> None:
    query = build_solar_conditions_query(
        observation_type="kp_index",
    )

    compiled = str(query)

    assert "solar_conditions.observation_type =" in compiled

    params = query.compile().params

    assert "kp_index" in params.values()


def test_start_time_filter_is_applied() -> None:
    start_time = datetime(
        2026,
        8,
        20,
        12,
        0,
        tzinfo=UTC,
    )

    query = build_solar_conditions_query(
        start_time=start_time,
    )

    compiled = str(query)

    assert "solar_conditions.observed_at >=" in compiled

    params = query.compile().params

    assert start_time in params.values()


def test_end_time_filter_is_applied() -> None:
    end_time = datetime(
        2026,
        8,
        21,
        12,
        0,
        tzinfo=UTC,
    )

    query = build_solar_conditions_query(
        end_time=end_time,
    )

    compiled = str(query)

    assert "solar_conditions.observed_at <=" in compiled

    params = query.compile().params

    assert end_time in params.values()


def test_limit_and_offset_are_applied() -> None:
    query = build_solar_conditions_query(
        limit=25,
        offset=50,
    )

    compiled = query.compile()

    values = set(compiled.params.values())

    assert 25 in values
    assert 50 in values


def test_list_solar_conditions_returns_scalar_results() -> None:
    session = MagicMock(spec=Session)

    first = MagicMock(spec=SolarCondition)
    second = MagicMock(spec=SolarCondition)

    scalar_result = MagicMock()
    scalar_result.all.return_value = [
        first,
        second,
    ]

    session.scalars.return_value = scalar_result

    result = list_solar_conditions(session)

    assert result == [
        first,
        second,
    ]

    session.scalars.assert_called_once()
    scalar_result.all.assert_called_once_with()
