import asyncio
import json
from collections.abc import AsyncGenerator
from time import perf_counter

import aiomqtt
from pydantic import ValidationError

from app.logging.logger import get_logger
from app.models.psk_reporter import (
    NormalizedPSKSpot,
    PSKReporterSpot,
)
from app.providers.base import (
    ProviderObservation,
    StreamingObservationProvider,
)

logger = get_logger(__name__)

DEFAULT_MQTT_HOST = "mqtt.pskreporter.info"
DEFAULT_MQTT_PORT = 1883
DEFAULT_MQTT_TOPIC = "pskr/filter/v2/20m/FT8/#"

DEFAULT_RECONNECT_DELAY_SECONDS = 5.0
DEFAULT_MAX_QUEUE_SIZE = 1_000


class PSKReporterError(RuntimeError):
    """Raised when PSK Reporter ingestion fails."""


class PSKReporterProvider(StreamingObservationProvider):
    name = "psk_reporter"

    def __init__(
        self,
        *,
        host: str = DEFAULT_MQTT_HOST,
        port: int = DEFAULT_MQTT_PORT,
        topic: str = DEFAULT_MQTT_TOPIC,
        reconnect_delay_seconds: float = DEFAULT_RECONNECT_DELAY_SECONDS,
        max_queue_size: int = DEFAULT_MAX_QUEUE_SIZE,
    ) -> None:
        self._host = host
        self._port = port
        self._topic = topic
        self._reconnect_delay_seconds = reconnect_delay_seconds
        self._max_queue_size = max_queue_size

    def _to_observation(
        self,
        spot: NormalizedPSKSpot,
    ) -> ProviderObservation:
        return ProviderObservation(
            provider=self.name,
            data=spot.model_dump(mode="json"),
        )

    def _parse_message(
        self,
        payload: bytes,
    ) -> NormalizedPSKSpot:
        try:
            decoded = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise PSKReporterError("PSK Reporter MQTT message contains invalid JSON") from exc

        if not isinstance(decoded, dict):
            raise PSKReporterError("PSK Reporter MQTT message must be a JSON object")

        try:
            spot = PSKReporterSpot.from_mqtt_payload(decoded)
            return spot.normalize()
        except (KeyError, ValidationError, TypeError, ValueError) as exc:
            raise PSKReporterError("PSK Reporter MQTT message could not be normalized") from exc

    async def _messages(
        self,
    ) -> AsyncGenerator[ProviderObservation]:
        started_at = perf_counter()
        record_count = 0

        async with aiomqtt.Client(
            hostname=self._host,
            port=self._port,
            max_queued_incoming_messages=self._max_queue_size,
        ) as client:
            connected_at = perf_counter()

            logger.info(
                "PSK Reporter MQTT connected",
                extra={
                    "provider": self.name,
                    "operation": "connect",
                    "host": self._host,
                    "port": self._port,
                    "duration_ms": round(
                        (connected_at - started_at) * 1000,
                        2,
                    ),
                },
            )

            await client.subscribe(self._topic)

            logger.info(
                "PSK Reporter MQTT subscribed",
                extra={
                    "provider": self.name,
                    "operation": "subscribe",
                    "topic": self._topic,
                },
            )

            try:
                async for message in client.messages:
                    try:
                        spot = self._parse_message(
                            bytes(message.payload),
                        )

                        record_count += 1

                        yield self._to_observation(spot)

                    except PSKReporterError as exc:
                        logger.warning(
                            "PSK Reporter message rejected",
                            extra={
                                "provider": self.name,
                                "operation": "message_validation",
                                "topic": str(message.topic),
                                "error": str(exc),
                            },
                        )

            finally:
                logger.info(
                    "PSK Reporter MQTT session ended",
                    extra={
                        "provider": self.name,
                        "operation": "stream",
                        "duration_ms": round(
                            (perf_counter() - connected_at) * 1000,
                            2,
                        ),
                        "record_count": record_count,
                    },
                )

    async def stream(
        self,
    ) -> AsyncGenerator[ProviderObservation]:
        while True:
            try:
                async for observation in self._messages():
                    yield observation

            except asyncio.CancelledError:
                logger.info(
                    "PSK Reporter stream cancelled",
                    extra={
                        "provider": self.name,
                        "operation": "stream",
                    },
                )
                raise

            except aiomqtt.MqttError as exc:
                logger.warning(
                    "PSK Reporter MQTT connection lost",
                    extra={
                        "provider": self.name,
                        "operation": "reconnect",
                        "error": str(exc),
                        "retry_seconds": self._reconnect_delay_seconds,
                    },
                )

                await asyncio.sleep(
                    self._reconnect_delay_seconds,
                )
