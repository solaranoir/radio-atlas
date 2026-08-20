import asyncio
import json
from collections.abc import AsyncIterator

import aiomqtt
import pytest

from app.providers.base import ProviderObservation
from app.providers.psk_reporter import (
    PSKReporterError,
    PSKReporterProvider,
)

VALID_PAYLOAD = {
    "sq": 71869170759,
    "f": 14075361,
    "md": "FT8",
    "rp": -5,
    "t": 1787168040,
    "t_tx": 1787168025,
    "sc": "EA5JLN",
    "sl": "IM99TN",
    "rc": "DL4JC",
    "rl": "JN39lh",
    "sa": 281,
    "ra": 230,
    "b": "20m",
}


def test_parse_message_returns_normalized_spot() -> None:
    provider = PSKReporterProvider()

    payload = json.dumps(VALID_PAYLOAD).encode()

    spot = provider._parse_message(payload)

    assert spot.sequence_number == 71869170759
    assert spot.sender_callsign.value == "EA5JLN"
    assert spot.receiver_callsign.value == "DL4JC"

    assert spot.sender_grid is not None
    assert spot.sender_grid.value == "IM99TN"

    assert spot.receiver_grid is not None
    assert spot.receiver_grid.value == "JN39LH"

    assert spot.frequency is not None
    assert spot.frequency.hz == 14075361

    assert spot.band is not None
    assert spot.band.value == "20m"

    assert spot.mode.value == "FT8"
    assert spot.snr_db == -5


def test_parse_message_rejects_invalid_json() -> None:
    provider = PSKReporterProvider()

    with pytest.raises(
        PSKReporterError,
        match="invalid JSON",
    ):
        provider._parse_message(b"definitely-not-json")


def test_parse_message_rejects_non_object_json() -> None:
    provider = PSKReporterProvider()

    payload = json.dumps(["this", "is", "a", "list"]).encode()

    with pytest.raises(
        PSKReporterError,
        match="must be a JSON object",
    ):
        provider._parse_message(payload)


def test_parse_message_rejects_missing_sender_callsign() -> None:
    provider = PSKReporterProvider()

    payload_data = VALID_PAYLOAD.copy()
    del payload_data["sc"]

    payload = json.dumps(payload_data).encode()

    with pytest.raises(
        PSKReporterError,
        match="could not be normalized",
    ):
        provider._parse_message(payload)


def test_parse_message_rejects_invalid_frequency() -> None:
    provider = PSKReporterProvider()

    payload_data = VALID_PAYLOAD.copy()
    payload_data["f"] = -1

    payload = json.dumps(payload_data).encode()

    with pytest.raises(
        PSKReporterError,
        match="could not be normalized",
    ):
        provider._parse_message(payload)


def test_to_observation_returns_provider_observation() -> None:
    provider = PSKReporterProvider()

    payload = json.dumps(VALID_PAYLOAD).encode()

    spot = provider._parse_message(payload)
    observation = provider._to_observation(spot)

    assert isinstance(
        observation,
        ProviderObservation,
    )

    assert observation.provider == "psk_reporter"

    assert observation.data["sequence_number"] == 71869170759

    assert observation.data["sender_callsign"] == {"value": "EA5JLN"}

    assert observation.data["receiver_callsign"] == {"value": "DL4JC"}

    assert observation.data["frequency"] == {"hz": 14075361}

    assert observation.data["band"] == {"value": "20m"}

    assert observation.data["mode"] == {"value": "FT8"}


@pytest.mark.asyncio
async def test_stream_yields_provider_observations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = PSKReporterProvider()

    spot = provider._parse_message(json.dumps(VALID_PAYLOAD).encode())

    observation = provider._to_observation(spot)

    async def fake_messages() -> AsyncIterator[ProviderObservation]:
        yield observation

    monkeypatch.setattr(
        provider,
        "_messages",
        fake_messages,
    )

    stream = provider.stream()

    result = await anext(stream)

    assert result.provider == "psk_reporter"
    assert result.data["sequence_number"] == 71869170759

    await stream.aclose()


@pytest.mark.asyncio
async def test_stream_propagates_cancelled_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = PSKReporterProvider()

    async def cancelled_messages() -> AsyncIterator[ProviderObservation]:
        raise asyncio.CancelledError

        if False:
            yield ProviderObservation(
                provider="unused",
                data={},
            )

    monkeypatch.setattr(
        provider,
        "_messages",
        cancelled_messages,
    )

    stream = provider.stream()

    with pytest.raises(asyncio.CancelledError):
        await anext(stream)


@pytest.mark.asyncio
async def test_stream_reconnects_after_mqtt_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = PSKReporterProvider(
        reconnect_delay_seconds=0,
    )

    spot = provider._parse_message(json.dumps(VALID_PAYLOAD).encode())

    observation = provider._to_observation(spot)

    attempts = 0

    async def fake_messages() -> AsyncIterator[ProviderObservation]:
        nonlocal attempts

        attempts += 1

        if attempts == 1:
            raise aiomqtt.MqttError("connection lost")

        yield observation

    monkeypatch.setattr(
        provider,
        "_messages",
        fake_messages,
    )

    stream = provider.stream()

    result = await anext(stream)

    assert attempts == 2
    assert result.provider == "psk_reporter"

    await stream.aclose()
