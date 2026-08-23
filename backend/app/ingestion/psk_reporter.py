from sqlalchemy.orm import Session

from app.ingestion.persistence import persist_observation
from app.observations.deduplication import ObservationDeduplicator
from app.observations.normalizer import normalize_observation
from app.providers.psk_reporter import PSKReporterProvider


async def run_psk_reporter_ingestion(
    session: Session,
    provider: PSKReporterProvider,
) -> None:
    deduplicator = ObservationDeduplicator()

    async for observation in provider.stream():
        normalized = normalize_observation(observation)

        if deduplicator.is_duplicate(normalized):
            continue

        persist_observation(
            session,
            normalized,
        )

        session.commit()
