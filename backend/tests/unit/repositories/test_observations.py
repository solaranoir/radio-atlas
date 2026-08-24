from datetime import UTC, datetime
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from app.infrastructure.database.models import Spot
from app.repositories.observations import (
    build_observations_query,
    list_observations,
)


def _compiled_query(**kwargs: object) -> str:
    query = build_observations_query(**kwargs)  # type: ignore[arg-type]

    return str(
        query.compile(
            compile_kwargs={
                "literal_binds": True,
            }
        )
    )


def test_default_query_orders_newest_first() -> None:
    query = build_observations_query()

    compiled = str(query)

    assert "ORDER BY spots.observed_at DESC" in compiled


def test_start_time_filter_is_applied() -> None:
    start_time = datetime(
        2026,
        8,
        20,
        12,
        0,
        tzinfo=UTC,
    )

    query = build_observations_query(
        start_time=start_time,
    )

    compiled = str(query)

    assert "spots.observed_at >=" in compiled

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

    query = build_observations_query(
        end_time=end_time,
    )

    compiled = str(query)

    assert "spots.observed_at <=" in compiled

    params = query.compile().params

    assert end_time in params.values()


def test_band_filter_is_applied() -> None:
    query = build_observations_query(
        band="20m",
    )

    compiled = str(query)

    assert "spots.band =" in compiled

    params = query.compile().params

    assert "20m" in params.values()


def test_limit_and_offset_are_applied() -> None:
    query = build_observations_query(
        limit=25,
        offset=50,
    )

    compiled = query.compile()

    values = set(compiled.params.values())

    assert 25 in values
    assert 50 in values


def test_list_observations_returns_scalar_results() -> None:
    session = MagicMock(spec=Session)

    first = MagicMock(spec=Spot)
    second = MagicMock(spec=Spot)

    scalar_result = MagicMock()
    scalar_result.all.return_value = [
        first,
        second,
    ]

    session.scalars.return_value = scalar_result

    result = list_observations(session)

    assert result == [
        first,
        second,
    ]

    session.scalars.assert_called_once()
    scalar_result.all.assert_called_once_with()
