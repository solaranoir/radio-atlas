import asyncio
from collections.abc import Awaitable, Callable
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.ingestion.runtime import run_ingestion_runtime
from app.main import lifespan


@pytest.mark.asyncio
async def test_runtime_starts_both_ingestion_schedules() -> None:
    with (
        patch(
            "app.ingestion.runtime.run_ingestion_schedules",
            new_callable=AsyncMock,
        ) as run_schedules,
        patch(
            "app.ingestion.runtime.ensure_providers",
        ),
        patch(
            "app.ingestion.runtime.NOAAProvider",
        ) as noaa_provider_cls,
        patch(
            "app.ingestion.runtime.PSKReporterProvider",
        ) as psk_provider_cls,
    ):
        noaa_provider = MagicMock()
        noaa_provider.aclose = AsyncMock()
        noaa_provider_cls.return_value = noaa_provider

        psk_provider = MagicMock()
        psk_provider_cls.return_value = psk_provider

        await run_ingestion_runtime()

    run_schedules.assert_awaited_once()

    args = run_schedules.await_args
    assert args is not None

    noaa_job = args.args[0]
    psk_job = args.args[1]

    assert callable(noaa_job)
    assert callable(psk_job)

    noaa_provider.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_runtime_noaa_job_uses_fresh_session() -> None:
    startup_session = MagicMock()
    job_session = MagicMock()

    startup_context = MagicMock()
    startup_context.__enter__.return_value = startup_session
    startup_context.__exit__.return_value = None

    job_context = MagicMock()
    job_context.__enter__.return_value = job_session
    job_context.__exit__.return_value = None

    async def run_schedules(
        noaa_job: Callable[[], Awaitable[int]],
        psk_job: Callable[[], Awaitable[None]],
    ) -> None:
        result = await noaa_job()
        assert result == 3

    with (
        patch(
            "app.ingestion.runtime.create_session",
        ) as create_session,
        patch(
            "app.ingestion.runtime.ensure_providers",
        ) as ensure_providers,
        patch(
            "app.ingestion.runtime.run_noaa_ingestion",
            new_callable=AsyncMock,
            return_value=3,
        ) as run_noaa_ingestion,
        patch(
            "app.ingestion.runtime.run_ingestion_schedules",
            side_effect=run_schedules,
        ),
        patch(
            "app.ingestion.runtime.NOAAProvider",
        ) as noaa_provider_cls,
        patch(
            "app.ingestion.runtime.PSKReporterProvider",
        ),
    ):
        create_session.side_effect = [
            startup_context,
            job_context,
        ]

        noaa_provider = MagicMock()
        noaa_provider.aclose = AsyncMock()
        noaa_provider_cls.return_value = noaa_provider

        await run_ingestion_runtime()

    assert create_session.call_count == 2
    ensure_providers.assert_called_once_with(startup_session)

    run_noaa_ingestion.assert_awaited_once_with(
        job_session,
        noaa_provider,
    )


@pytest.mark.asyncio
async def test_runtime_psk_job_uses_session() -> None:
    startup_session = MagicMock()
    job_session = MagicMock()

    startup_context = MagicMock()
    startup_context.__enter__.return_value = startup_session
    startup_context.__exit__.return_value = None

    job_context = MagicMock()
    job_context.__enter__.return_value = job_session
    job_context.__exit__.return_value = None

    async def run_schedules(
        noaa_job: Callable[[], Awaitable[int]],
        psk_job: Callable[[], Awaitable[None]],
    ) -> None:
        await psk_job()

    with (
        patch(
            "app.ingestion.runtime.create_session",
        ) as create_session,
        patch(
            "app.ingestion.runtime.ensure_providers",
        ) as ensure_providers,
        patch(
            "app.ingestion.runtime.run_psk_reporter_ingestion",
            new_callable=AsyncMock,
        ) as run_psk_ingestion,
        patch(
            "app.ingestion.runtime.run_ingestion_schedules",
            side_effect=run_schedules,
        ),
        patch(
            "app.ingestion.runtime.NOAAProvider",
        ) as noaa_provider_cls,
        patch(
            "app.ingestion.runtime.PSKReporterProvider",
        ) as psk_provider_cls,
    ):
        create_session.side_effect = [
            startup_context,
            job_context,
        ]

        noaa_provider = MagicMock()
        noaa_provider.aclose = AsyncMock()
        noaa_provider_cls.return_value = noaa_provider

        psk_provider = MagicMock()
        psk_provider_cls.return_value = psk_provider

        await run_ingestion_runtime()

    assert create_session.call_count == 2
    ensure_providers.assert_called_once_with(startup_session)

    run_psk_ingestion.assert_awaited_once_with(
        job_session,
        psk_provider,
    )


@pytest.mark.asyncio
async def test_runtime_closes_noaa_provider_on_shutdown() -> None:
    with (
        patch(
            "app.ingestion.runtime.run_ingestion_schedules",
            new_callable=AsyncMock,
        ),
        patch(
            "app.ingestion.runtime.ensure_providers",
        ),
        patch(
            "app.ingestion.runtime.NOAAProvider",
        ) as noaa_provider_cls,
        patch(
            "app.ingestion.runtime.PSKReporterProvider",
        ),
    ):
        noaa_provider = MagicMock()
        noaa_provider.aclose = AsyncMock()
        noaa_provider_cls.return_value = noaa_provider

        await run_ingestion_runtime()

    noaa_provider.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_lifespan_starts_ingestion_task() -> None:
    started = asyncio.Event()
    cancelled = asyncio.Event()

    async def fake_runtime() -> None:
        started.set()

        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            cancelled.set()
            raise

    with patch(
        "app.main.run_ingestion_runtime",
        side_effect=fake_runtime,
    ) as runtime:
        async with lifespan(MagicMock()):
            await asyncio.wait_for(
                started.wait(),
                timeout=1,
            )

            assert runtime.called

    assert cancelled.is_set()


@pytest.mark.asyncio
async def test_lifespan_cancels_ingestion_on_shutdown() -> None:
    task_started = asyncio.Event()
    task_cancelled = asyncio.Event()

    async def fake_runtime() -> None:
        task_started.set()

        try:
            while True:
                await asyncio.sleep(60)
        except asyncio.CancelledError:
            task_cancelled.set()
            raise

    with patch(
        "app.main.run_ingestion_runtime",
        side_effect=fake_runtime,
    ):
        async with lifespan(MagicMock()):
            await asyncio.wait_for(
                task_started.wait(),
                timeout=1,
            )

        assert task_cancelled.is_set()
