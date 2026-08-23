import asyncio
from collections.abc import AsyncIterator
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.ingestion.psk_reporter import run_psk_reporter_ingestion
from app.providers.base import ProviderObservation
from app.providers.psk_reporter import PSKReporterProvider


async def _stream_observations(
    observations: list[ProviderObservation],
) -> AsyncIterator[ProviderObservation]:
    for observation in observations:
        yield observation


async def cancelled_stream() -> AsyncIterator[ProviderObservation]:
    raise asyncio.CancelledError
    yield  # pragma: no cover


async def failing_stream(
    observation: ProviderObservation,
) -> AsyncIterator[ProviderObservation]:
    yield observation
    raise RuntimeError("PSK Reporter stream failed")


@pytest.mark.asyncio
async def test_persists_normalized_streamed_spots() -> None:
    session = MagicMock(spec=Session)
    provider = MagicMock(spec=PSKReporterProvider)

    raw_observation = ProviderObservation(
        provider="psk_reporter",
        data={
            "sequence_number": 1,
            "sender_callsign": {"value": "EA5JLN"},
            "receiver_callsign": {"value": "DL4JC"},
            "mode": {"value": "FT8"},
            "observed_at": "2026-08-20T20:35:44Z",
        },
    )

    normalized_observation = MagicMock()

    provider.stream.return_value = _stream_observations([raw_observation])

    with (
        patch(
            "app.ingestion.psk_reporter.normalize_observation",
            return_value=normalized_observation,
        ) as normalize,
        patch(
            "app.ingestion.psk_reporter.persist_observation",
        ) as persist,
        patch(
            "app.ingestion.psk_reporter.ObservationDeduplicator",
        ) as deduplicator_class,
    ):
        deduplicator_class.return_value.is_duplicate.return_value = False

        await run_psk_reporter_ingestion(
            session,
            provider,
        )

    normalize.assert_called_once_with(raw_observation)
    persist.assert_called_once_with(
        session,
        normalized_observation,
    )


@pytest.mark.asyncio
async def test_skips_duplicate_streamed_spots() -> None:
    session = MagicMock(spec=Session)
    provider = MagicMock(spec=PSKReporterProvider)

    first = ProviderObservation(
        provider="psk_reporter",
        data={"sequence_number": 1},
    )
    duplicate = ProviderObservation(
        provider="psk_reporter",
        data={"sequence_number": 1},
    )

    first_normalized = MagicMock()
    duplicate_normalized = MagicMock()

    provider.stream.return_value = _stream_observations(
        [
            first,
            duplicate,
        ]
    )

    with (
        patch(
            "app.ingestion.psk_reporter.normalize_observation",
            side_effect=[
                first_normalized,
                duplicate_normalized,
            ],
        ),
        patch(
            "app.ingestion.psk_reporter.persist_observation",
        ) as persist,
        patch(
            "app.ingestion.psk_reporter.ObservationDeduplicator",
        ) as deduplicator_class,
    ):
        deduplicator_class.return_value.is_duplicate.side_effect = [
            False,
            True,
        ]

        await run_psk_reporter_ingestion(
            session,
            provider,
        )

    persist.assert_called_once_with(
        session,
        first_normalized,
    )


@pytest.mark.asyncio
async def test_commits_persisted_spots() -> None:
    session = MagicMock(spec=Session)
    provider = MagicMock(spec=PSKReporterProvider)

    observations = [
        ProviderObservation(
            provider="psk_reporter",
            data={"sequence_number": 1},
        ),
        ProviderObservation(
            provider="psk_reporter",
            data={"sequence_number": 2},
        ),
    ]

    provider.stream.return_value = _stream_observations(observations)

    with (
        patch(
            "app.ingestion.psk_reporter.normalize_observation",
            side_effect=[
                MagicMock(),
                MagicMock(),
            ],
        ),
        patch(
            "app.ingestion.psk_reporter.persist_observation",
        ),
        patch(
            "app.ingestion.psk_reporter.ObservationDeduplicator",
        ) as deduplicator_class,
    ):
        deduplicator_class.return_value.is_duplicate.return_value = False

        await run_psk_reporter_ingestion(
            session,
            provider,
        )

    assert session.commit.call_count == 2


@pytest.mark.asyncio
async def test_propagates_cancellation_cleanly() -> None:
    session = MagicMock(spec=Session)
    provider = MagicMock(spec=PSKReporterProvider)

    provider.stream.return_value = cancelled_stream()

    with (
        patch(
            "app.ingestion.psk_reporter.normalize_observation",
        ) as normalize,
        patch(
            "app.ingestion.psk_reporter.persist_observation",
        ) as persist,
        pytest.raises(asyncio.CancelledError),
    ):
        await run_psk_reporter_ingestion(
            session,
            provider,
        )

    normalize.assert_not_called()
    persist.assert_not_called()
    session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_stream_failure_propagates_without_committing_failed_item() -> None:
    session = MagicMock(spec=Session)
    provider = MagicMock(spec=PSKReporterProvider)

    first = ProviderObservation(
        provider="psk_reporter",
        data={"sequence_number": 1},
    )

    provider.stream.return_value = failing_stream(first)

    normalized = MagicMock()

    with (
        patch(
            "app.ingestion.psk_reporter.normalize_observation",
            return_value=normalized,
        ),
        patch(
            "app.ingestion.psk_reporter.persist_observation",
        ) as persist,
        patch(
            "app.ingestion.psk_reporter.ObservationDeduplicator",
        ) as deduplicator_class,
    ):
        deduplicator_class.return_value.is_duplicate.return_value = False

        with pytest.raises(
            RuntimeError,
            match="PSK Reporter stream failed",
        ):
            await run_psk_reporter_ingestion(
                session,
                provider,
            )

    persist.assert_called_once_with(
        session,
        normalized,
    )
    session.commit.assert_called_once_with()
