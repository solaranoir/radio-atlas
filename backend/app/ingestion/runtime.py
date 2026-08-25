from app.infrastructure.database.session import create_session
from app.ingestion.noaa import run_noaa_ingestion
from app.ingestion.persistence import ensure_providers
from app.ingestion.psk_reporter import run_psk_reporter_ingestion
from app.ingestion.scheduler import run_ingestion_schedules
from app.providers.noaa import NOAAProvider
from app.providers.psk_reporter import PSKReporterProvider


async def run_ingestion_runtime() -> None:
    noaa_provider = NOAAProvider()
    psk_reporter_provider = PSKReporterProvider()

    with create_session() as session:
        ensure_providers(session)
        session.commit()

    async def noaa_job() -> int:
        with create_session() as session:
            return await run_noaa_ingestion(
                session,
                noaa_provider,
            )

    async def psk_reporter_job() -> None:
        with create_session() as session:
            await run_psk_reporter_ingestion(
                session,
                psk_reporter_provider,
            )

    try:
        await run_ingestion_schedules(
            noaa_job,
            psk_reporter_job,
        )
    finally:
        await noaa_provider.aclose()
