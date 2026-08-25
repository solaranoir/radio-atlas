from sqlalchemy.orm import Session

from app.health import psk_reporter_health
from app.ingestion.persistence import persist_observation
from app.observations.deduplication import ObservationDeduplicator
from app.observations.normalizer import normalize_observation
from app.providers.psk_reporter import PSKReporterProvider


async def run_psk_reporter_ingestion(
    session: Session,
    provider: PSKReporterProvider,
) -> None:
    deduplicator = ObservationDeduplicator()

    async for provider_observation in provider.stream():
        observation = normalize_observation(
            provider_observation,
        )

        if deduplicator.is_duplicate(observation):
            continue

        persist_observation(
            session,
            observation,
        )

        session.commit()

        psk_reporter_health.record_success()
