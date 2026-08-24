from datetime import datetime

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.infrastructure.database.models import Spot


def build_observations_query(
    *,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    band: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> Select[tuple[Spot]]:
    query = select(Spot)

    if start_time is not None:
        query = query.where(
            Spot.observed_at >= start_time,
        )

    if end_time is not None:
        query = query.where(
            Spot.observed_at <= end_time,
        )

    if band is not None:
        query = query.where(
            Spot.band == band,
        )

    return (
        query.order_by(
            Spot.observed_at.desc(),
        )
        .limit(limit)
        .offset(offset)
    )


def list_observations(
    session: Session,
    *,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    band: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Spot]:
    query = build_observations_query(
        start_time=start_time,
        end_time=end_time,
        band=band,
        limit=limit,
        offset=offset,
    )

    return list(session.scalars(query).all())
