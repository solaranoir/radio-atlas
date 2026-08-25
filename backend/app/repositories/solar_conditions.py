from datetime import datetime

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.infrastructure.database.models import SolarCondition


def build_solar_conditions_query(
    *,
    observation_type: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    limit: int = 100,
    offset: int = 0,
) -> Select[tuple[SolarCondition]]:
    query = select(SolarCondition)

    if observation_type is not None:
        query = query.where(
            SolarCondition.observation_type == observation_type,
        )

    if start_time is not None:
        query = query.where(
            SolarCondition.observed_at >= start_time,
        )

    if end_time is not None:
        query = query.where(
            SolarCondition.observed_at <= end_time,
        )

    return (
        query.order_by(
            SolarCondition.observed_at.desc(),
        )
        .limit(limit)
        .offset(offset)
    )


def list_solar_conditions(
    session: Session,
    *,
    observation_type: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[SolarCondition]:
    query = build_solar_conditions_query(
        observation_type=observation_type,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=offset,
    )

    return list(session.scalars(query).all())
