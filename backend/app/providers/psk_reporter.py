import asyncio
import json
import logging
from collections.abc import AsyncIterator

import aiomqtt
from pydantic import ValidationError

from app.models.psk_reporter import (
    NormalizedPSKSpot,
    PSKReporterSpot,
)

logger = logging.getLogger(__name__)

DEFAULT_MQTT_HOST = "mqtt.pskreporter.info"
DEFAULT_MQTT_PORT = 1883
DEFAULT_MQTT_TOPIC = "pskr/filter/v2/20m/FT8/#"

DEFAULT_RECONNECT_DELAY_SECONDS = 5.0
DEFAULT_MAX_QUEUE_SIZE = 1_000


class PSKReporterError(RuntimeError):
    """Raised when PSK Reporter ingestion fails."""


class PSKReporterProvider:
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
    ) -> AsyncIterator[NormalizedPSKSpot]:
        async with aiomqtt.Client(
            hostname=self._host,
            port=self._port,
            max_queued_incoming_messages=self._max_queue_size,
        ) as client:
            logger.info(
                "PSK Reporter MQTT connected",
                extra={
                    "provider": self.name,
                    "operation": "connect",
                    "host": self._host,
                    "port": self._port,
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

            async for message in client.messages:
                try:
                    yield self._parse_message(bytes(message.payload))
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

    async def stream(
        self,
    ) -> AsyncIterator[NormalizedPSKSpot]:
        while True:
            try:
                async for spot in self._messages():
                    yield spot

            except asyncio.CancelledError:
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
