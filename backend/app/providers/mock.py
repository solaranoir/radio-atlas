from app.providers.base import ObservationProvider, ProviderObservation


class MockObservationProvider(ObservationProvider):
    def __init__(
        self,
        observations: list[ProviderObservation] | None = None,
    ) -> None:
        self._observations = observations or []

    @property
    def name(self) -> str:
        return "mock"

    async def fetch(self) -> list[ProviderObservation]:
        return self._observations
