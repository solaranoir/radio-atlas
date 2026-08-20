import asyncio

import pytest

from app.providers.base import ProviderObservation
from app.providers.psk_reporter import PSKReporterProvider


@pytest.mark.integration
@pytest.mark.asyncio
async def test_provider_fetches_live_spot() -> None:
    provider = PSKReporterProvider()

    stream = provider.stream()

    try:
        observation = await asyncio.wait_for(
            anext(stream),
            timeout=30,
        )

        assert isinstance(
            observation,
            ProviderObservation,
        )

        assert observation.provider == "psk_reporter"

        assert "sender_callsign" in observation.data
        assert "receiver_callsign" in observation.data
        assert "frequency" in observation.data
        assert "band" in observation.data
        assert "mode" in observation.data

    finally:
        await stream.aclose()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_spot_contains_expected_fields() -> None:
    provider = PSKReporterProvider()

    stream = provider.stream()

    try:
        observation = await asyncio.wait_for(
            anext(stream),
            timeout=30,
        )

        data = observation.data

        assert data["sender_callsign"]["value"]

        assert data["receiver_callsign"]["value"]

        assert data["frequency"]["hz"] > 0

        assert data["band"]["value"]

        assert data["mode"]["value"]

        snr_db = data["snr_db"]

        assert snr_db is None or isinstance(snr_db, int)

    finally:
        await stream.aclose()


@pytest.mark.integration
def test_provider_configuration() -> None:
    provider = PSKReporterProvider()

    assert provider.name == "psk_reporter"

    assert provider._host
    assert provider._port > 0
    assert provider._topic


@pytest.mark.integration
@pytest.mark.asyncio
async def test_provider_processes_multiple_messages() -> None:
    provider = PSKReporterProvider()

    stream = provider.stream()

    count = 0

    try:
        async for observation in stream:
            count += 1

            assert observation.provider == "psk_reporter"

            if count >= 5:
                break

        assert count == 5

    finally:
        await stream.aclose()
