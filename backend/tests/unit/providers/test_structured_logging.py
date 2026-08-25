import asyncio
from collections.abc import AsyncIterator
from unittest.mock import AsyncMock, MagicMock, patch

import aiomqtt
import pytest

from app.providers.base import ProviderObservation
from app.providers.noaa import NOAAProvider
from app.providers.psk_reporter import (
    PSKReporterError,
    PSKReporterProvider,
)


@pytest.mark.asyncio
async def test_noaa_completion_log_contains_structured_fields() -> None:
    provider = NOAAProvider()

    observation = ProviderObservation(
        provider="noaa",
        data={"value": 1},
    )

    with (
        patch.object(
            provider,
            "_fetch_solar_flux",
            new_callable=AsyncMock,
            return_value=[observation],
        ),
        patch.object(
            provider,
            "_fetch_kp",
            new_callable=AsyncMock,
            return_value=[],
        ),
        patch.object(
            provider,
            "_fetch_sunspots",
            new_callable=AsyncMock,
            return_value=[],
        ),
        patch.object(
            provider,
            "_fetch_aurora",
            new_callable=AsyncMock,
            return_value=[],
        ),
        patch.object(
            provider,
            "_fetch_magnetic_field",
            new_callable=AsyncMock,
            return_value=[],
        ),
        patch.object(
            provider,
            "_fetch_solar_wind",
            new_callable=AsyncMock,
            return_value=[],
        ),
        patch(
            "app.providers.noaa.perf_counter",
            side_effect=[10.0, 10.125],
        ),
        patch(
            "app.providers.noaa.logger.info",
        ) as logger_info,
    ):
        result = await provider.fetch()

    assert result == [observation]

    completion_call = next(
        call for call in logger_info.call_args_list if call.args[0] == "NOAA ingestion completed"
    )

    extra = completion_call.kwargs["extra"]

    assert extra["provider"] == "noaa"
    assert extra["operation"] == "fetch"
    assert extra["duration_ms"] == 125.0
    assert extra["record_count"] == 1


@pytest.mark.asyncio
async def test_noaa_failure_log_contains_structured_fields() -> None:
    provider = NOAAProvider()

    failure = RuntimeError("NOAA exploded")

    with (
        patch.object(
            provider,
            "_fetch_solar_flux",
            new_callable=AsyncMock,
            side_effect=failure,
        ),
        patch(
            "app.providers.noaa.perf_counter",
            side_effect=[20.0, 20.25],
        ),
        patch(
            "app.providers.noaa.logger.error",
        ) as logger_error,
        pytest.raises(
            RuntimeError,
            match="NOAA exploded",
        ),
    ):
        await provider.fetch()

    logger_error.assert_called_once()

    call = logger_error.call_args

    assert call is not None
    assert call.args[0] == "NOAA ingestion failed"

    extra = call.kwargs["extra"]

    assert extra["provider"] == "noaa"
    assert extra["operation"] == "fetch"
    assert extra["duration_ms"] == 250.0
    assert extra["error"] == "NOAA exploded"

    assert call.kwargs["exc_info"] is True


@pytest.mark.asyncio
async def test_psk_connection_log_contains_structured_fields() -> None:
    provider = PSKReporterProvider()

    class EmptyMessages:
        def __aiter__(self) -> "EmptyMessages":
            return self

        async def __anext__(self) -> object:
            raise StopAsyncIteration

    class FakeClient:
        messages = EmptyMessages()

        async def __aenter__(self) -> "FakeClient":
            return self

        async def __aexit__(
            self,
            exc_type: object,
            exc: BaseException | None,
            traceback: object,
        ) -> None:
            return None

        async def subscribe(
            self,
            topic: str,
        ) -> None:
            return None

    with (
        patch(
            "app.providers.psk_reporter.aiomqtt.Client",
            return_value=FakeClient(),
        ),
        patch(
            "app.providers.psk_reporter.perf_counter",
            side_effect=[10.0, 10.075, 10.200],
        ),
        patch(
            "app.providers.psk_reporter.logger.info",
        ) as logger_info,
    ):
        observations = [observation async for observation in provider._messages()]

    assert observations == []

    connection_call = next(
        call for call in logger_info.call_args_list if call.args[0] == "PSK Reporter MQTT connected"
    )

    extra = connection_call.kwargs["extra"]

    assert extra["provider"] == "psk_reporter"
    assert extra["operation"] == "connect"
    assert extra["duration_ms"] == 75.0


@pytest.mark.asyncio
async def test_psk_session_end_log_contains_duration_and_record_count() -> None:
    provider = PSKReporterProvider()

    class FakeMessage:
        payload = b'{"spot": "valid"}'
        topic = "pskr/test"

    class FakeMessages:
        def __init__(self) -> None:
            self._messages = [FakeMessage(), FakeMessage()]

        def __aiter__(self) -> "FakeMessages":
            return self

        async def __anext__(self) -> "FakeMessage":
            if not self._messages:
                raise StopAsyncIteration

            return self._messages.pop(0)

    class FakeClient:
        def __init__(self) -> None:
            self.messages = FakeMessages()

        async def __aenter__(self) -> "FakeClient":
            return self

        async def __aexit__(
            self,
            exc_type: object,
            exc: BaseException | None,
            traceback: object,
        ) -> None:
            return None

        async def subscribe(
            self,
            topic: str,
        ) -> None:
            return None

    observation = ProviderObservation(
        provider="psk_reporter",
        data={"sequence_number": 1},
    )

    with (
        patch(
            "app.providers.psk_reporter.aiomqtt.Client",
            return_value=FakeClient(),
        ),
        patch.object(
            provider,
            "_parse_message",
            return_value=MagicMock(),
        ),
        patch.object(
            provider,
            "_to_observation",
            return_value=observation,
        ),
        patch(
            "app.providers.psk_reporter.perf_counter",
            side_effect=[5.0, 5.025, 5.525],
        ),
        patch(
            "app.providers.psk_reporter.logger.info",
        ) as logger_info,
    ):
        observations = [item async for item in provider._messages()]

    assert observations == [
        observation,
        observation,
    ]

    session_call = next(
        call
        for call in logger_info.call_args_list
        if call.args[0] == "PSK Reporter MQTT session ended"
    )

    extra = session_call.kwargs["extra"]

    assert extra["provider"] == "psk_reporter"
    assert extra["operation"] == "stream"
    assert extra["duration_ms"] == 500.0
    assert extra["record_count"] == 2


@pytest.mark.asyncio
async def test_rejected_psk_message_logs_error_without_stopping_stream() -> None:
    provider = PSKReporterProvider()

    class FakeMessage:
        def __init__(
            self,
            payload: bytes,
        ) -> None:
            self.payload = payload
            self.topic = "pskr/test"

    class FakeMessages:
        def __init__(self) -> None:
            self._messages = [
                FakeMessage(b"bad"),
                FakeMessage(b"good"),
            ]

        def __aiter__(self) -> "FakeMessages":
            return self

        async def __anext__(self) -> "FakeMessage":
            if not self._messages:
                raise StopAsyncIteration

            return self._messages.pop(0)

    class FakeClient:
        def __init__(self) -> None:
            self.messages = FakeMessages()

        async def __aenter__(self) -> "FakeClient":
            return self

        async def __aexit__(
            self,
            exc_type: object,
            exc: BaseException | None,
            traceback: object,
        ) -> None:
            return None

        async def subscribe(
            self,
            topic: str,
        ) -> None:
            return None

    observation = ProviderObservation(
        provider="psk_reporter",
        data={"sequence_number": 1},
    )

    with (
        patch(
            "app.providers.psk_reporter.aiomqtt.Client",
            return_value=FakeClient(),
        ),
        patch.object(
            provider,
            "_parse_message",
            side_effect=[
                PSKReporterError("invalid spot"),
                MagicMock(),
            ],
        ),
        patch.object(
            provider,
            "_to_observation",
            return_value=observation,
        ),
        patch(
            "app.providers.psk_reporter.perf_counter",
            side_effect=[1.0, 1.1, 1.5],
        ),
        patch(
            "app.providers.psk_reporter.logger.warning",
        ) as logger_warning,
    ):
        observations = [item async for item in provider._messages()]

    assert observations == [observation]

    rejection_call = next(
        call
        for call in logger_warning.call_args_list
        if call.args[0] == "PSK Reporter message rejected"
    )

    extra = rejection_call.kwargs["extra"]

    assert extra["provider"] == "psk_reporter"
    assert extra["operation"] == "message_validation"
    assert extra["topic"] == "pskr/test"
    assert extra["error"] == "invalid spot"


@pytest.mark.asyncio
async def test_mqtt_reconnect_failure_logs_error_and_retry_delay() -> None:
    provider = PSKReporterProvider(
        reconnect_delay_seconds=7.5,
    )

    async def failing_messages() -> AsyncIterator[ProviderObservation]:
        if False:
            yield ProviderObservation(
                provider="psk_reporter",
                data={},
            )

        raise aiomqtt.MqttError("connection lost")

    with (
        patch.object(
            provider,
            "_messages",
            side_effect=failing_messages,
        ),
        patch(
            "app.providers.psk_reporter.asyncio.sleep",
            new_callable=AsyncMock,
            side_effect=asyncio.CancelledError,
        ),
        patch(
            "app.providers.psk_reporter.logger.warning",
        ) as logger_warning,
        pytest.raises(asyncio.CancelledError),
    ):
        async for _ in provider.stream():
            pass

    logger_warning.assert_called_once()

    call = logger_warning.call_args

    assert call is not None
    assert call.args[0] == "PSK Reporter MQTT connection lost"

    extra = call.kwargs["extra"]

    assert extra["provider"] == "psk_reporter"
    assert extra["operation"] == "reconnect"
    assert extra["error"] == "connection lost"
    assert extra["retry_seconds"] == 7.5


@pytest.mark.asyncio
async def test_psk_cancellation_is_logged_and_propagates() -> None:
    provider = PSKReporterProvider()

    async def cancelled_messages() -> AsyncIterator[ProviderObservation]:
        if False:
            yield ProviderObservation(
                provider="psk_reporter",
                data={},
            )

        raise asyncio.CancelledError

    with (
        patch.object(
            provider,
            "_messages",
            side_effect=cancelled_messages,
        ),
        patch(
            "app.providers.psk_reporter.logger.info",
        ) as logger_info,
        pytest.raises(asyncio.CancelledError),
    ):
        async for _ in provider.stream():
            pass

    cancellation_call = next(
        call
        for call in logger_info.call_args_list
        if call.args[0] == "PSK Reporter stream cancelled"
    )

    extra = cancellation_call.kwargs["extra"]

    assert extra["provider"] == "psk_reporter"
    assert extra["operation"] == "stream"
