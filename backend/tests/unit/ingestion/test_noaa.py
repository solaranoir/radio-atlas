from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.ingestion.noaa import run_noaa_ingestion
from app.providers.base import ProviderObservation
from app.providers.noaa import NOAAProvider


@pytest.mark.asyncio
async def test_persists_normalized_noaa_observations() -> None:
    session = MagicMock(spec=Session)
    provider = MagicMock(spec=NOAAProvider)

    raw_observation = ProviderObservation(
        provider="noaa",
        data={
            "observed_at": "2026-08-20T12:00:00Z",
            "kp_index": 2.0,
        },
    )

    normalized_observation = MagicMock()

    provider.fetch = AsyncMock(
        return_value=[raw_observation],
    )

    with (
        patch(
            "app.ingestion.noaa.normalize_observation",
            return_value=normalized_observation,
        ) as normalize,
        patch(
            "app.ingestion.noaa.persist_observation",
        ) as persist,
        patch(
            "app.ingestion.noaa.ObservationDeduplicator",
        ) as deduplicator_class,
    ):
        deduplicator_class.return_value.is_duplicate.return_value = False

        await run_noaa_ingestion(
            session,
            provider,
        )

    normalize.assert_called_once_with(raw_observation)
    persist.assert_called_once_with(
        session,
        normalized_observation,
    )


@pytest.mark.asyncio
async def test_skips_duplicate_noaa_observations() -> None:
    session = MagicMock(spec=Session)
    provider = MagicMock(spec=NOAAProvider)

    first = ProviderObservation(
        provider="noaa",
        data={"kp_index": 2.0},
    )
    duplicate = ProviderObservation(
        provider="noaa",
        data={"kp_index": 2.0},
    )

    first_normalized = MagicMock()
    duplicate_normalized = MagicMock()

    provider.fetch = AsyncMock(
        return_value=[
            first,
            duplicate,
        ],
    )

    with (
        patch(
            "app.ingestion.noaa.normalize_observation",
            side_effect=[
                first_normalized,
                duplicate_normalized,
            ],
        ),
        patch(
            "app.ingestion.noaa.persist_observation",
        ) as persist,
        patch(
            "app.ingestion.noaa.ObservationDeduplicator",
        ) as deduplicator_class,
    ):
        deduplicator_class.return_value.is_duplicate.side_effect = [
            False,
            True,
        ]

        result = await run_noaa_ingestion(
            session,
            provider,
        )

    persist.assert_called_once_with(
        session,
        first_normalized,
    )
    assert result == 1


@pytest.mark.asyncio
async def test_commits_once_after_noaa_batch() -> None:
    session = MagicMock(spec=Session)
    provider = MagicMock(spec=NOAAProvider)

    observations = [
        ProviderObservation(
            provider="noaa",
            data={"kp_index": 2.0},
        ),
        ProviderObservation(
            provider="noaa",
            data={"flux_sfu": 150.0},
        ),
        ProviderObservation(
            provider="noaa",
            data={"sunspot_number": 120},
        ),
    ]

    provider.fetch = AsyncMock(
        return_value=observations,
    )

    with (
        patch(
            "app.ingestion.noaa.normalize_observation",
            side_effect=[
                MagicMock(),
                MagicMock(),
                MagicMock(),
            ],
        ),
        patch(
            "app.ingestion.noaa.persist_observation",
        ),
        patch(
            "app.ingestion.noaa.ObservationDeduplicator",
        ) as deduplicator_class,
    ):
        deduplicator_class.return_value.is_duplicate.return_value = False

        await run_noaa_ingestion(
            session,
            provider,
        )

    session.commit.assert_called_once_with()


@pytest.mark.asyncio
async def test_returns_number_of_persisted_noaa_observations() -> None:
    session = MagicMock(spec=Session)
    provider = MagicMock(spec=NOAAProvider)

    observations = [
        ProviderObservation(
            provider="noaa",
            data={"kp_index": 2.0},
        ),
        ProviderObservation(
            provider="noaa",
            data={"flux_sfu": 150.0},
        ),
        ProviderObservation(
            provider="noaa",
            data={"sunspot_number": 120},
        ),
    ]

    provider.fetch = AsyncMock(
        return_value=observations,
    )

    with (
        patch(
            "app.ingestion.noaa.normalize_observation",
            side_effect=[
                MagicMock(),
                MagicMock(),
                MagicMock(),
            ],
        ),
        patch(
            "app.ingestion.noaa.persist_observation",
        ),
        patch(
            "app.ingestion.noaa.ObservationDeduplicator",
        ) as deduplicator_class,
    ):
        deduplicator_class.return_value.is_duplicate.side_effect = [
            False,
            True,
            False,
        ]

        result = await run_noaa_ingestion(
            session,
            provider,
        )

    assert result == 2


@pytest.mark.asyncio
async def test_provider_failure_propagates_without_commit() -> None:
    session = MagicMock(spec=Session)
    provider = MagicMock(spec=NOAAProvider)

    provider.fetch = AsyncMock(
        side_effect=RuntimeError("NOAA unavailable"),
    )

    with (
        patch(
            "app.ingestion.noaa.normalize_observation",
        ) as normalize,
        patch(
            "app.ingestion.noaa.persist_observation",
        ) as persist,
        pytest.raises(
            RuntimeError,
            match="NOAA unavailable",
        ),
    ):
        await run_noaa_ingestion(
            session,
            provider,
        )

    normalize.assert_not_called()
    persist.assert_not_called()
    session.commit.assert_not_called()
