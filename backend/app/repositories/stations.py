# app/repositories/stations.py

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.infrastructure.database.models import Station


def build_stations_query(
    *,
    callsign: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> Select[tuple[Station]]:
    query = select(Station)

    if callsign is not None:
        query = query.where(
            Station.callsign == callsign.upper(),
        )

    return (
        query.order_by(
            Station.callsign.asc(),
        )
        .limit(limit)
        .offset(offset)
    )


def list_stations(
    session: Session,
    *,
    callsign: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Station]:
    query = build_stations_query(
        callsign=callsign,
        limit=limit,
        offset=offset,
    )

    return list(session.scalars(query).all())
