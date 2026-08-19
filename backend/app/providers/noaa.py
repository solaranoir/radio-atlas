from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from app.logging.logger import get_logger
from app.models.noaa import (
    AuroraForecast,
    AuroraGridCell,
    KpIndex,
    SolarFlux,
    SolarMagneticField,
    SolarWind,
    SunspotNumber,
)
from app.providers.base import (
    ObservationProvider,
    ProviderObservation,
)
from app.services.http import JsonHttpClient

logger = get_logger(__name__)

DEFAULT_NOAA_BASE_URL = "https://services.swpc.noaa.gov"


class NOAAResponseError(RuntimeError):
    """Raised when NOAA returns an unusable payload."""


class NOAAProvider(ObservationProvider):
    def __init__(
        self,
        *,
        http_client: JsonHttpClient | None = None,
        base_url: str = DEFAULT_NOAA_BASE_URL,
    ) -> None:
        self._http_client = http_client or JsonHttpClient()
        self._owns_http_client = http_client is None
        self._base_url = base_url.rstrip("/")

    @property
    def name(self) -> str:
        return "noaa"

    def _url(self, path: str) -> str:
        return f"{self._base_url}/{path.lstrip('/')}"

    def _latest_record(
        self,
        payload: Any,
        *,
        feed: str,
        timestamp_field: str = "time_tag",
    ) -> dict[str, Any]:
        if isinstance(payload, dict):
            return payload

        if not isinstance(payload, list):
            raise NOAAResponseError(
                f"NOAA {feed} response must be an object or list"
            )

        if not payload:
            raise NOAAResponseError(
                f"NOAA {feed} response was empty"
            )

        records = [
            record
            for record in payload
            if isinstance(record, dict)
            and record.get(timestamp_field) is not None
        ]

        if not records:
            raise NOAAResponseError(
                f"NOAA {feed} response contained no valid records"
            )

        return max(
            records,
            key=lambda record: str(record[timestamp_field]),
        )

    async def fetch(self) -> list[ProviderObservation]:
        logger.info(
            "NOAA ingestion started",
            extra={
                "provider": self.name,
                "operation": "fetch",
            },
        )

        observations: list[ProviderObservation] = []

        observations.extend(await self._fetch_solar_flux())
        observations.extend(await self._fetch_kp())
        observations.extend(await self._fetch_sunspots())
        observations.extend(await self._fetch_aurora())
        observations.extend(await self._fetch_magnetic_field())
        observations.extend(await self._fetch_solar_wind())

        logger.info(
            "NOAA ingestion completed",
            extra={
                "provider": self.name,
                "operation": "fetch",
                "record_count": len(observations),
            },
        )

        return observations

    async def _fetch_solar_flux(
        self,
    ) -> list[ProviderObservation]:
        url = self._url("json/f107_cm_flux.json")

        payload = await self._http_client.get_json(url)

        record = self._latest_record(
            payload,
            feed="solar_flux",
        )

        try:
            solar_flux = SolarFlux(
                observed_at=record["time_tag"],
                frequency_mhz=record["frequency"],
                flux_sfu=record["flux"],
                reporting_schedule=record["reporting_schedule"],
                ninety_day_mean=record["ninety_day_mean"],
            )
        except (
            KeyError,
            TypeError,
            ValueError,
            ValidationError,
        ) as exc:
            raise self._validation_error(
                feed="solar_flux",
                error=exc,
            ) from exc

        logger.info(
            "NOAA feed ingested",
            extra={
                "provider": self.name,
                "operation": "ingest",
                "feed": "solar_flux",
                "record_count": 1,
            },
        )

        return [self._to_observation(solar_flux)]

    async def _fetch_kp(
        self,
    ) -> list[ProviderObservation]:
        url = self._url("json/planetary_k_index_1m.json")

        payload = await self._http_client.get_json(url)

        record = self._latest_record(
            payload,
            feed="kp",
        )

        try:
            kp = KpIndex(
                observed_at=record["time_tag"],
                kp_index=record["kp_index"],
                estimated_kp=record["estimated_kp"],
                category=record["kp"],
            )
        except (
            KeyError,
            TypeError,
            ValueError,
            ValidationError,
        ) as exc:
            raise self._validation_error(
                feed="kp",
                error=exc,
            ) from exc

        logger.info(
            "NOAA feed ingested",
            extra={
                "provider": self.name,
                "operation": "ingest",
                "feed": "kp",
                "record_count": 1,
            },
        )

        return [self._to_observation(kp)]

    async def _fetch_sunspots(
        self,
    ) -> list[ProviderObservation]:
        url = self._url(
            "json/solar-cycle/swpc_observed_ssn.json"
        )
        payload = await self._http_client.get_json(url)

        record = self._latest_record(
            payload,
            feed="sunspots",
            timestamp_field="Obsdate",
        )

        try:
            sunspots = SunspotNumber(
                observed_at=record["Obsdate"],
                sunspot_number=record["swpc_ssn"],
            )
        except (
            KeyError,
            TypeError,
            ValueError,
            ValidationError,
        ) as exc:
            raise self._validation_error(
                feed="sunspots",
                error=exc,
            ) from exc

        logger.info(
            "NOAA feed ingested",
            extra={
                "provider": self.name,
                "operation": "ingest",
                "feed": "sunspots",
                "record_count": 1,
            },
        )

        return [self._to_observation(sunspots)]

    async def _fetch_magnetic_field(
        self,
   ) -> list[ProviderObservation]:
        url = self._url("json/rtsw/rtsw_mag_1m.json")

        payload = await self._http_client.get_json(url)

        record = self._latest_record(
            payload,
            feed="magnetic_field",
        )

        try:
            magnetic_field = SolarMagneticField(
                observed_at=record["time_tag"],
                total_field_nt=record["bt"],
                bz_gsm_nt=record["bz_gsm"],
                data_quality=record["overall_quality"],
            )
        except (
            KeyError,
            TypeError,
            ValueError,
            ValidationError,
        ) as exc:
            raise self._validation_error(
                feed="magnetic_field",
                error=exc,
            ) from exc

        logger.info(
            "NOAA feed ingested",
            extra={
                "provider": self.name,
                "operation": "ingest",
                "feed": "magnetic_field",
                "record_count": 1,
            },
        )

        return [self._to_observation(magnetic_field)]

    async def _fetch_solar_wind(
       self,
   ) -> list[ProviderObservation]:
       url = self._url("json/rtsw/rtsw_wind_1m.json")

       payload = await self._http_client.get_json(url)

       record = self._latest_record(
           payload,
           feed="solar_wind",
       )

       try:
           solar_wind = SolarWind(
               observed_at=record["time_tag"],
               proton_speed_kms=record["proton_speed"],
               proton_density_cm3=record["proton_density"],
               proton_temperature_k=record["proton_temperature"],
               data_quality=record["overall_quality"],
           )
       except (
           KeyError,
           TypeError,
           ValueError,
           ValidationError,
       ) as exc:
           raise self._validation_error(
               feed="solar_wind",
               error=exc,
           ) from exc

       logger.info(
           "NOAA feed ingested",
           extra={
               "provider": self.name,
               "operation": "ingest",
               "feed": "solar_wind",
               "record_count": 1,
           },
       )

       return [self._to_observation(solar_wind)]

    def _to_observation(
        self,
        model: SolarFlux
        | KpIndex
        | SunspotNumber
        | AuroraForecast
        | SolarMagneticField
        | SolarWind,
    ) -> ProviderObservation:
        return ProviderObservation(
            provider=self.name,
            data=model.model_dump(mode="json"),
        )

    def _validation_error(
        self,
        *,
        feed: str,
        error: Exception,
    ) -> NOAAResponseError:
        logger.error(
            "NOAA response validation failed",
            extra={
                "provider": self.name,
                "operation": "response_validation",
                "feed": feed,
                "error": str(error),
            },
        )

        return NOAAResponseError(
            f"NOAA {feed} response could not be normalized"
        )

    async def _fetch_aurora(
        self,
    ) -> list[ProviderObservation]:
        url = (
            f"{self._base_url}"
            "/json/ovation_aurora_latest.json"
        )

        payload = await self._http_client.get_json(url)

        if not isinstance(payload, dict):
            raise NOAAResponseError(
                "NOAA aurora response must be an object"
            )

        try:
            coordinates = payload["coordinates"]

            cells = [
                AuroraGridCell(
                    longitude=row[0],
                    latitude=row[1],
                    aurora=row[2],
                )
                for row in coordinates
            ]

            forecast = AuroraForecast(
                observed_at=payload["Observation Time"],
                forecast_at=payload["Forecast Time"],
                cells=cells,
            )

        except (
            KeyError,
            IndexError,
            TypeError,
            ValidationError,
        ) as exc:
            raise self._validation_error(
                feed="aurora",
                error=exc,
            ) from exc

        logger.info(
            "NOAA feed ingested",
            extra={
                "provider": self.name,
                "operation": "ingest",
                "feed": "aurora",
                "record_count": len(cells),
            },
        )

        return [self._to_observation(forecast)]

    async def aclose(self) -> None:
        if self._owns_http_client:
            await self._http_client.aclose()

    async def __aenter__(self) -> NOAAProvider:
        return self

    async def __aexit__(
        self,
        exc_type: object,
        exc: BaseException | None,
        traceback: object,
    ) -> None:
        await self.aclose()
