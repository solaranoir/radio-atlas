import pytest

from app.providers.noaa import NOAAProvider


@pytest.mark.asyncio
@pytest.mark.integration
async def test_noaa_provider_fetches_live_data() -> None:
    async with NOAAProvider() as provider:
        observations = await provider.fetch()

    assert len(observations) == 6

    assert all(observation.provider == "noaa" for observation in observations)

    assert any("flux_sfu" in observation.data for observation in observations)

    assert any("kp_index" in observation.data for observation in observations)

    assert any("sunspot_number" in observation.data for observation in observations)

    assert any("cells" in observation.data for observation in observations)

    assert any("total_field_nt" in observation.data for observation in observations)

    assert any("proton_speed_kms" in observation.data for observation in observations)
