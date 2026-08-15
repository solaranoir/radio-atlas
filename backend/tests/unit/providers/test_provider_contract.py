import pytest

from app.providers import (
    MockObservationProvider,
    ObservationProvider,
    ProviderObservation,
)


def test_mock_provider_implements_observation_provider() -> None:
    provider = MockObservationProvider()

    assert isinstance(provider, ObservationProvider)


def test_mock_provider_has_name() -> None:
    provider = MockObservationProvider()

    assert provider.name == "mock"


@pytest.mark.asyncio
async def test_mock_provider_returns_observations() -> None:
    expected = [
        ProviderObservation(
            provider="mock",
            data={"value": 42},
        )
    ]

    provider = MockObservationProvider(observations=expected)

    observations = await provider.fetch()

    assert observations == expected
