import pytest

from app.providers import (
    MockObservationProvider,
    ObservationProvider,
    PollingObservationProvider,
    ProviderObservation,
    StreamingObservationProvider,
)
from app.providers.noaa import NOAAProvider
from app.providers.psk_reporter import PSKReporterProvider


def test_noaa_provider_implements_common_provider_contract() -> None:
    assert issubclass(
        NOAAProvider,
        ObservationProvider,
    )


def test_noaa_provider_implements_polling_contract() -> None:
    assert issubclass(
        NOAAProvider,
        PollingObservationProvider,
    )


def test_psk_reporter_implements_common_provider_contract() -> None:
    assert issubclass(
        PSKReporterProvider,
        ObservationProvider,
    )


def test_psk_reporter_implements_streaming_contract() -> None:
    assert issubclass(
        PSKReporterProvider,
        StreamingObservationProvider,
    )


def test_mock_provider_implements_polling_contract() -> None:
    provider = MockObservationProvider()

    assert isinstance(provider, PollingObservationProvider)


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

    provider = MockObservationProvider(
        observations=expected,
    )

    observations = await provider.fetch()

    assert observations == expected
