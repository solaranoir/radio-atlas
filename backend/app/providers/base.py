from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ProviderObservation:
    provider: str
    data: dict[str, Any]


class ObservationProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the unique provider name."""


class PollingObservationProvider(ObservationProvider):
    @abstractmethod
    async def fetch(self) -> list[ProviderObservation]:
        """Fetch a batch of observations from the external provider."""


class StreamingObservationProvider(ObservationProvider):
    @abstractmethod
    def stream(self) -> AsyncIterator[ProviderObservation]:
        """Stream observations from the external provider."""
