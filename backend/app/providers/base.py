from abc import ABC, abstractmethod
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

    @abstractmethod
    async def fetch(self) -> list[ProviderObservation]:
        """Fetch observations from the external provider."""
