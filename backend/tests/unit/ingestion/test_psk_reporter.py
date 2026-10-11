import asyncio
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.domain import SpotObservation
from app.ingestion.psk_reporter import run_psk_reporter_ingestion
from app.providers.base import ProviderObservation
from app.providers.psk_reporter import PSKReporterProvider


async def stream(count: int, fail: bool = False) -> AsyncIterator[ProviderObservation]:
    for index in range(count):
        yield ProviderObservation(provider="psk_reporter", data={"sequence_number": index})
    if fail:
        raise RuntimeError("stream failed")


def normalize(raw: ProviderObservation) -> SpotObservation:
    return SpotObservation(
        provider="psk_reporter",
        sequence_number=raw.data["sequence_number"],
        observed_at=datetime(2026, 1, 1, tzinfo=UTC),
        sender_callsign="TEST",
        receiver_callsign="OTHER",
        mode="FT8",
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("count,sizes", [(0, []), (1, [1]), (205, [100, 100, 5])])
async def test_bounded_batches_flush_tail(count: int, sizes: list[int]) -> None:
    session = MagicMock(spec=Session)
    provider = MagicMock(spec=PSKReporterProvider)
    provider.stream.return_value = stream(count)
    with (
        patch("app.ingestion.psk_reporter.normalize_observation", side_effect=normalize),
        patch("app.ingestion.psk_reporter.persist_spot_batch") as persist,
    ):
        await run_psk_reporter_ingestion(session, provider)
    assert [len(call.args[1]) for call in persist.call_args_list] == sizes
    assert session.commit.call_count == len(sizes)


@pytest.mark.asyncio
async def test_failed_commit_rolls_back_without_retry() -> None:
    session = MagicMock(spec=Session)
    session.commit.side_effect = RuntimeError("database unavailable")
    provider = MagicMock(spec=PSKReporterProvider)
    provider.stream.return_value = stream(100)
    with (
        patch("app.ingestion.psk_reporter.normalize_observation", side_effect=normalize),
        patch("app.ingestion.psk_reporter.persist_spot_batch") as persist,
        pytest.raises(RuntimeError, match="database unavailable"),
    ):
        await run_psk_reporter_ingestion(session, provider)
    persist.assert_called_once()
    session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_stream_failure_preserves_accepted_tail() -> None:
    session = MagicMock(spec=Session)
    provider = MagicMock(spec=PSKReporterProvider)
    provider.stream.return_value = stream(1, fail=True)
    with (
        patch("app.ingestion.psk_reporter.normalize_observation", side_effect=normalize),
        patch("app.ingestion.psk_reporter.persist_spot_batch"),
        pytest.raises(RuntimeError, match="stream failed"),
    ):
        await run_psk_reporter_ingestion(session, provider)
    session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_sparse_flush_keeps_stream_open_and_cancellation_closes_it() -> None:
    session = MagicMock(spec=Session)
    provider = MagicMock(spec=PSKReporterProvider)
    written = asyncio.Event()
    closed = asyncio.Event()
    loop = asyncio.get_running_loop()

    async def sparse() -> AsyncIterator[ProviderObservation]:
        try:
            yield ProviderObservation(provider="psk_reporter", data={"sequence_number": 1})
            await asyncio.Event().wait()
        finally:
            closed.set()

    provider.stream.return_value = sparse()
    with (
        patch("app.ingestion.psk_reporter.normalize_observation", side_effect=normalize),
        patch(
            "app.ingestion.psk_reporter.persist_spot_batch",
            side_effect=lambda *_: loop.call_soon_threadsafe(written.set),
        ),
    ):
        task = asyncio.create_task(
            run_psk_reporter_ingestion(session, provider, flush_seconds=0.01)
        )
        try:
            await asyncio.wait_for(written.wait(), 1)
            assert not closed.is_set()
        finally:
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
    assert closed.is_set()
    session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_duplicates_are_excluded_from_batch() -> None:
    session = MagicMock(spec=Session)
    provider = MagicMock(spec=PSKReporterProvider)
    provider.stream.return_value = stream(2)
    item = normalize(ProviderObservation(provider="psk_reporter", data={"sequence_number": 1}))
    with (
        patch("app.ingestion.psk_reporter.normalize_observation", return_value=item),
        patch("app.ingestion.psk_reporter.persist_spot_batch") as persist,
    ):
        await run_psk_reporter_ingestion(session, provider)
    assert persist.call_args.args[1] == [item]


def test_bulk_write_looks_up_provider_once_and_executes_once() -> None:
    from app.ingestion.persistence import persist_spot_batch

    session = MagicMock(spec=Session)
    session.scalar.return_value = 7
    items = [
        normalize(ProviderObservation(provider="psk_reporter", data={"sequence_number": i}))
        for i in range(100)
    ]
    persist_spot_batch(session, items)
    session.scalar.assert_called_once()
    session.execute.assert_called_once()
    rows = session.execute.call_args.args[1]
    assert len(rows) == 100
    assert all(row["provider_id"] == 7 and "provider" not in row for row in rows)
    session.commit.assert_not_called()
