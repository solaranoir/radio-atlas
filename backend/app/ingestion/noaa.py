from sqlalchemy.orm import Session

from app.ingestion.persistence import persist_observation
from app.observations.deduplication import ObservationDeduplicator
from app.observations.normalizer import normalize_observation
from app.providers.noaa import NOAAProvider


async def run_noaa_ingestion(
    session: Session,
    provider: NOAAProvider,
) -> int:
    deduplicator = ObservationDeduplicator()

    observations = await provider.fetch()

    persisted = 0

    for observation in observations:
        normalized = normalize_observation(observation)

        if deduplicator.is_duplicate(normalized):
            continue

        persist_observation(
            session,
            normalized,
        )
        persisted += 1

    session.commit()

    return persisted
