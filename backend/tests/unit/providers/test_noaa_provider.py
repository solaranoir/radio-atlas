from typing import Any

import pytest

from app.providers.noaa import NOAAProvider, NOAAResponseError


class FakeJsonHttpClient:
    def __init__(self, payload: Any) -> None:
        self.payload = payload

    async def get_json(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> Any:
        return self.payload

    async def aclose(self) -> None:
        pass


@pytest.mark.asyncio
async def test_fetch_solar_flux() -> None:
    payload = [
        {
            "time_tag": "2026-08-18T22:00:00",
            "frequency": 2800,
            "flux": 124.0,
            "reporting_schedule": "Afternoon",
            "avg_begin_date": None,
            "ninety_day_mean": None,
            "rec_count": None,
        }
    ]

    http_client = FakeJsonHttpClient(payload)

    provider = NOAAProvider(
        http_client=http_client,  # type: ignore[arg-type]
    )

    observations = await provider._fetch_solar_flux()

    assert len(observations) == 1

    observation = observations[0]

    assert observation.provider == "noaa"
    assert observation.data["observed_at"] == "2026-08-18T22:00:00"
    assert observation.data["frequency_mhz"] == 2800
    assert observation.data["flux_sfu"] == 124.0
    assert observation.data["reporting_schedule"] == "Afternoon"
    assert observation.data["ninety_day_mean"] is None


@pytest.mark.asyncio
async def test_fetch_kp() -> None:
    payload = [
        {
            "time_tag": "2026-08-19T17:31:00",
            "kp_index": 1,
            "estimated_kp": 0.67,
            "kp": "1M",
        }
    ]

    provider = NOAAProvider(
        http_client=FakeJsonHttpClient(payload),  # type: ignore[arg-type]
    )

    observations = await provider._fetch_kp()

    assert len(observations) == 1

    observation = observations[0]

    assert observation.provider == "noaa"
    assert observation.data["observed_at"] == "2026-08-19T17:31:00"
    assert observation.data["kp_index"] == 1.0
    assert observation.data["estimated_kp"] == 0.67
    assert observation.data["category"] == "1M"


@pytest.mark.asyncio
async def test_fetch_sunspots() -> None:
    payload = [
        {
            "Obsdate": "2026-08-19T00:00:00",
            "swpc_ssn": 66,
        }
    ]

    provider = NOAAProvider(
        http_client=FakeJsonHttpClient(payload),  # type: ignore[arg-type]
    )

    observations = await provider._fetch_sunspots()

    assert len(observations) == 1

    observation = observations[0]

    assert observation.provider == "noaa"
    assert observation.data["observed_at"] == "2026-08-19T00:00:00"
    assert observation.data["sunspot_number"] == 66


@pytest.mark.asyncio
async def test_fetch_magnetic_field() -> None:
    payload = [
        {
            "time_tag": "2026-08-19T17:30:01",
            "bt": 3.56,
            "bz_gsm": -0.41,
            "overall_quality": 0,
        }
    ]

    provider = NOAAProvider(
        http_client=FakeJsonHttpClient(payload),  # type: ignore[arg-type]
    )

    observations = await provider._fetch_magnetic_field()

    assert len(observations) == 1

    observation = observations[0]

    assert observation.data["observed_at"] == "2026-08-19T17:30:01"
    assert observation.data["total_field_nt"] == 3.56
    assert observation.data["bz_gsm_nt"] == -0.41
    assert observation.data["data_quality"] == 0


@pytest.mark.asyncio
async def test_fetch_solar_wind() -> None:
    payload = [
        {
            "time_tag": "2026-08-19T17:29:07",
            "proton_speed": 546.1,
            "proton_density": 2.32,
            "proton_temperature": 164930,
            "overall_quality": 0,
        }
    ]

    provider = NOAAProvider(
        http_client=FakeJsonHttpClient(payload),  # type: ignore[arg-type]
    )

    observations = await provider._fetch_solar_wind()

    assert len(observations) == 1

    observation = observations[0]

    assert observation.data["observed_at"] == "2026-08-19T17:29:07"
    assert observation.data["proton_speed_kms"] == 546.1
    assert observation.data["proton_density_cm3"] == 2.32
    assert observation.data["proton_temperature_k"] == 164930.0
    assert observation.data["data_quality"] == 0


@pytest.mark.asyncio
async def test_fetch_aurora() -> None:
    payload = {
        "Observation Time": "2026-08-19T13:10:00Z",
        "Forecast Time": "2026-08-19T13:59:00Z",
        "Data Format": "[Longitude, Latitude, Aurora]",
        "coordinates": [
            [0, -90, 5],
            [1, -89, 3],
        ],
    }

    provider = NOAAProvider(
        http_client=FakeJsonHttpClient(payload),  # type: ignore[arg-type]
    )

    observations = await provider._fetch_aurora()

    assert len(observations) == 1

    observation = observations[0]

    assert observation.data["observed_at"] == "2026-08-19T13:10:00Z"
    assert observation.data["forecast_at"] == "2026-08-19T13:59:00Z"
    assert len(observation.data["cells"]) == 2

    assert observation.data["cells"][0] == {
        "longitude": 0.0,
        "latitude": -90.0,
        "aurora": 5,
    }


@pytest.mark.asyncio
async def test_fetch_returns_all_noaa_observations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = NOAAProvider(
        http_client=FakeJsonHttpClient({}),  # type: ignore[arg-type]
    )

    async def solar_flux() -> list[dict[str, Any]]:
        return []

    async def kp() -> list[dict[str, Any]]:
        return []

    async def sunspots() -> list[dict[str, Any]]:
        return []

    async def aurora() -> list[dict[str, Any]]:
        return []

    async def magnetic() -> list[dict[str, Any]]:
        return []

    async def wind() -> list[dict[str, Any]]:
        return []

    monkeypatch.setattr(provider, "_fetch_solar_flux", solar_flux)
    monkeypatch.setattr(provider, "_fetch_kp", kp)
    monkeypatch.setattr(provider, "_fetch_sunspots", sunspots)
    monkeypatch.setattr(provider, "_fetch_aurora", aurora)
    monkeypatch.setattr(provider, "_fetch_magnetic_field", magnetic)
    monkeypatch.setattr(provider, "_fetch_solar_wind", wind)

    observations = await provider.fetch()

    assert observations == []


@pytest.mark.asyncio
async def test_solar_flux_missing_required_field() -> None:
    payload = [
        {
            "time_tag": "2026-08-18T22:00:00",
            "frequency": 2800,
            # flux missing
            "reporting_schedule": "Afternoon",
            "ninety_day_mean": None,
        }
    ]

    provider = NOAAProvider(
        http_client=FakeJsonHttpClient(payload),  # type: ignore[arg-type]
    )

    with pytest.raises(NOAAResponseError):
        await provider._fetch_solar_flux()


@pytest.mark.asyncio
async def test_kp_missing_required_field() -> None:
    payload = [
        {
            "time_tag": "2026-08-19T17:31:00",
            "kp_index": 1,
            # estimated_kp missing
            "kp": "1M",
        }
    ]

    provider = NOAAProvider(
        http_client=FakeJsonHttpClient(payload),  # type: ignore[arg-type]
    )

    with pytest.raises(NOAAResponseError):
        await provider._fetch_kp()


@pytest.mark.asyncio
async def test_sunspots_missing_required_field() -> None:
    payload = [
        {
            "Obsdate": "2026-08-19T00:00:00",
            # swpc_ssn missing
        }
    ]

    provider = NOAAProvider(
        http_client=FakeJsonHttpClient(payload),  # type: ignore[arg-type]
    )

    with pytest.raises(NOAAResponseError):
        await provider._fetch_sunspots()


@pytest.mark.asyncio
async def test_magnetic_field_missing_required_field() -> None:
    payload = [
        {
            "time_tag": "2026-08-19T17:30:01",
            "bt": 3.56,
            # bz_gsm missing
            "overall_quality": 0,
        }
    ]

    provider = NOAAProvider(
        http_client=FakeJsonHttpClient(payload),  # type: ignore[arg-type]
    )

    with pytest.raises(NOAAResponseError):
        await provider._fetch_magnetic_field()


@pytest.mark.asyncio
async def test_solar_wind_missing_required_field() -> None:
    payload = [
        {
            "time_tag": "2026-08-19T17:29:07",
            "proton_speed": 546.1,
            # proton_density missing
            "proton_temperature": 164930,
            "overall_quality": 0,
        }
    ]

    provider = NOAAProvider(
        http_client=FakeJsonHttpClient(payload),  # type: ignore[arg-type]
    )

    with pytest.raises(NOAAResponseError):
        await provider._fetch_solar_wind()


@pytest.mark.asyncio
async def test_aurora_invalid_payload_shape() -> None:
    provider = NOAAProvider(
        http_client=FakeJsonHttpClient([]),  # type: ignore[arg-type]
    )

    with pytest.raises(NOAAResponseError):
        await provider._fetch_aurora()


@pytest.mark.asyncio
async def test_aurora_invalid_coordinate() -> None:
    payload = {
        "Observation Time": "2026-08-19T13:10:00Z",
        "Forecast Time": "2026-08-19T13:59:00Z",
        "coordinates": [
            [0, -95, 5],  # invalid latitude
        ],
    }

    provider = NOAAProvider(
        http_client=FakeJsonHttpClient(payload),  # type: ignore[arg-type]
    )

    with pytest.raises(NOAAResponseError):
        await provider._fetch_aurora()
