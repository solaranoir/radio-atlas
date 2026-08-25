from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from app.infrastructure.database.models import Station
from app.repositories.stations import (
    build_stations_query,
    list_stations,
)


def test_default_query_orders_by_callsign_ascending() -> None:
    query = build_stations_query()

    compiled = str(query)

    assert "ORDER BY stations.callsign ASC" in compiled


def test_callsign_filter_is_applied() -> None:
    query = build_stations_query(
        callsign="KK7QEA",
    )

    compiled = str(query)

    assert "stations.callsign =" in compiled

    params = query.compile().params

    assert "KK7QEA" in params.values()


def test_callsign_filter_normalizes_lowercase_to_uppercase() -> None:
    query = build_stations_query(
        callsign="kk7qea",
    )

    params = query.compile().params

    assert "KK7QEA" in params.values()
    assert "kk7qea" not in params.values()


def test_limit_and_offset_are_applied() -> None:
    query = build_stations_query(
        limit=25,
        offset=50,
    )

    compiled = query.compile()

    values = set(compiled.params.values())

    assert 25 in values
    assert 50 in values


def test_list_stations_returns_scalar_results() -> None:
    session = MagicMock(spec=Session)

    first = MagicMock(spec=Station)
    second = MagicMock(spec=Station)

    scalar_result = MagicMock()
    scalar_result.all.return_value = [
        first,
        second,
    ]

    session.scalars.return_value = scalar_result

    result = list_stations(session)

    assert result == [
        first,
        second,
    ]

    session.scalars.assert_called_once()
    scalar_result.all.assert_called_once_with()
