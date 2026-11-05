import asyncio
import os
import signal
from unittest.mock import MagicMock, patch

import pytest

from app.ingestion.worker import run_worker


async def _forever() -> None:
    await asyncio.Event().wait()


@pytest.mark.asyncio
@pytest.mark.parametrize(("retention_days", "expected"), [(14, True), (0, False)])
async def test_worker_starts_retention_only_when_enabled(
    retention_days: int, expected: bool
) -> None:
    settings = MagicMock(radio_atlas_spot_retention_days=retention_days)
    retention = MagicMock(side_effect=lambda days: _forever())

    with (
        patch("app.ingestion.worker.run_ingestion_runtime", side_effect=_forever),
        patch("app.ingestion.worker.run_aggregation_runtime", side_effect=_forever),
        patch("app.ingestion.worker.run_retention_runtime", retention),
        patch("app.ingestion.worker.get_settings", return_value=settings),
    ):
        asyncio.get_running_loop().call_later(0.05, os.kill, os.getpid(), signal.SIGTERM)
        await asyncio.wait_for(run_worker(), timeout=5)

    assert retention.called is expected
    if expected:
        retention.assert_called_once_with(retention_days)
