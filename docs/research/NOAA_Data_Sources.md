# NOAA Data Sources

## Purpose

This document identifies the NOAA Space Weather Prediction Center (SWPC)
data sources used by SolaraSphere: Radio Atlas.

The goal of Phase 1 is to establish a minimal set of NOAA data feeds that
support the Radio Atlas product pillars:

- Observe
- Explain
- Predict
- Replay
- Explore

Only data required for live propagation visualization and explanation are
included in the initial implementation.

Forecasting and historical products are documented separately for future
phases.

---

## Phase 1 Selected NOAA Endpoints

| Radio Atlas Model | NOAA Endpoint | Status |
| --- | --- | --- |
| `SolarFlux` | `f107_cm_flux.json` | Selected |
| `KpIndex` | `planetary_k_index_1m.json` | Selected |
| `SunspotNumber` | `sunspot_report.json` | Selected |
| `AuroraForecast` | `ovation_aurora_latest.json` | Selected |
| `SolarMagneticField` | `rtsw_mag_1m.json` | Selected |
| `SolarWind` | `rtsw_wind_1m.json` | Selected |

---

## Solar Flux

### Selected endpoint

https://services.swpc.noaa.gov/json/f107_cm_flux.json

### Why this endpoint was selected

This endpoint provides the canonical F10.7 measurement at 2800 MHz.

The payload is simple, consistent, and directly maps to a strongly typed
application model.

### Example response

```json
{
    "time_tag": "2026-08-15T20:00:00",
    "frequency": 2800,
    "flux": 117,
    "reporting_schedule": "Noon",
    "avg_begin_date": "2026-05-18T20:00:00",
    "ninety_day_mean": 131,
    "rec_count": 90
}
```

### Required fields

| NOAA field | Radio Atlas field |
| --- | --- |
| `time_tag` | `observed_at` |
| `frequency` | `frequency_mhz` |
| `flux` | `flux_sfu` |
| `reporting_schedule` | `reporting_schedule` |
| `ninety_day_mean` | `ninety_day_mean` |

### Refresh interval

| Property | Value |
| --- | --- |
| Update frequency | Daily |
| Recommended polling | Every 12 hours |

---

## Planetary K Index

### Selected endpoint

https://services.swpc.noaa.gov/json/planetary_k_index_1m.json

### Why this endpoint was selected

This endpoint provides near real time global geomagnetic activity.

Planetary Kp is a better fit for Radio Atlas than station-specific
measurements such as Boulder K.

### Example response

```json
{
    "time_tag": "2026-08-15T15:58:00",
    "kp_index": 1,
    "estimated_kp": 0.67,
    "kp": "1M"
}
```

### Required fields

| NOAA field | Radio Atlas field |
| --- | --- |
| `time_tag` | `observed_at` |
| `kp_index` | `kp_index` |
| `estimated_kp` | `estimated_kp` |
| `kp` | `category` |

### Refresh interval

| Property | Value |
| --- | --- |
| Update frequency | 1 minute |
| Recommended polling | 5 minutes |

---

## Sunspot Number

### Selected endpoint

https://services.swpc.noaa.gov/json/sunspot_report.json

### Why this endpoint was selected

This endpoint provides current observed sunspot activity.

Historical and solar-cycle products were intentionally excluded from
Phase 1.

### Required fields

| NOAA field | Radio Atlas field |
| --- | --- |
| `time_tag` | `observed_at` |
| `sunspot_number` | `sunspot_number` |

### Refresh interval

| Property | Value |
| --- | --- |
| Update frequency | Daily |
| Recommended polling | Every 12 hours |

---

## Aurora

### Selected Endpoint
`https://services.swpc.noaa.gov/json/ovation_aurora_latest.json`

### Purpose

The OVATION endpoint provides a geographic auroral forecast suitable for
rendering as a spatial layer on the Radio Weather Globe.

The response contains an observation timestamp, a forecast timestamp, and
a grid of geographic coordinates with associated auroral values.

### Example Response

```json
{
    "Observation Time": "2026-08-15T22:10:00Z",
    "Forecast Time": "2026-08-15T23:26:00Z",
    "Data Format": "[Longitude, Latitude, Aurora]",
    "coordinates": [
        [0, -90, 3]
    ]
}
```

### Response Structure

| NOAA field | Description |
| --- | --- |
| `Observation Time` | Time associated with the observations used to generate the forecast |
| `Forecast Time` | Time for which the auroral forecast applies |
| `Data Format` | Documents the ordering of values in each coordinate tuple |
| `coordinates` | Geographic forecast grid containing longitude, latitude, and auroral value |

Each coordinate entry follows the format:

```text
[longitude, latitude, aurora]
```

Example:

```text
[0, -90, 3]
```

represents:

| Value | Meaning |
| --- | --- |
| `0` | Longitude |
| `-90` | Latitude |
| `3` | Aurora value |

### Recommended Radio Atlas Mapping

| NOAA field | Radio Atlas field |
| --- | --- |
| `Observation Time` | `observed_at` |
| `Forecast Time` | `forecast_at` |
| `coordinates` | `cells` |
| Coordinate `[0]` | `longitude` |
| Coordinate `[1]` | `latitude` |
| Coordinate `[2]` | `aurora` |

### Recommended Model Shape

The OVATION payload should be represented as one auroral forecast
containing many geographic grid cells rather than thousands of independent
provider observations.

```python
@dataclass(frozen=True)
class AuroraGridCell:
    longitude: float
    latitude: float
    aurora: int


@dataclass(frozen=True)
class AuroraForecast:
    observed_at: datetime
    forecast_at: datetime
    cells: list[AuroraGridCell]
```

This structure preserves the geographic relationship between grid cells
and is better suited for rendering the forecast as a layer on the Radio
Weather Globe.

### Phase 1 Recommendation

**Selected.**

The OVATION feed provides directly visualizable geographic space-weather
data and supports both the Observe and Explore product pillars.

---

## Solar Magnetic Field

### Selected endpoint

https://services.swpc.noaa.gov/json/rtsw/rtsw_mag_1m.json

### Why this endpoint was selected

Interplanetary magnetic field data helps explain propagation changes.

The southward magnetic field component (`bz_gsm`) is especially important
because it strongly influences geomagnetic storms.

### Example response

```json
{
    "bt": 4.33,
    "bz_gsm": 1.52,
    "overall_quality": 0
}
```

### Required fields

| NOAA field | Radio Atlas field |
| --- | --- |
| `time_tag` | `observed_at` |
| `bt` | `total_field_nt` |
| `bz_gsm` | `bz_gsm_nt` |
| `overall_quality` | `data_quality` |

### Refresh interval

| Property | Value |
| --- | --- |
| Update frequency | 1 minute |
| Recommended polling | 5 minutes |

---

## Solar Wind

### Selected endpoint

https://services.swpc.noaa.gov/json/rtsw/rtsw_wind_1m.json

### Why this endpoint was selected

Solar wind speed and density are critical inputs for understanding
geomagnetic disturbances and ionospheric changes.

### Example response

```json
{
    "proton_speed": 348.2,
    "proton_temperature": 52631,
    "proton_density": 2.75
}
```

### Required fields

| NOAA field | Radio Atlas field |
| --- | --- |
| `time_tag` | `observed_at` |
| `proton_speed` | `proton_speed_kms` |
| `proton_density` | `proton_density_cm3` |
| `proton_temperature` | `proton_temperature_k` |
| `overall_quality` | `data_quality` |

### Refresh interval

| Property | Value |
| --- | --- |
| Update frequency | 1 minute |
| Recommended polling | 5 minutes |

---

## Forecast Endpoints (Future Phases)

| NOAA Endpoint | Future Use |
| --- | --- |
| `45-day-forecast.json` | Long-range propagation |
| `predicted_f107cm_flux.json` | F10.7 forecasting |
| `solar_probabilities.json` | Flare prediction |
| `27-day-outlook.txt` | Medium-range planning |
| `predicted_monthly_sunspot_number.json` | Solar cycle forecasting |
| `enlil_time_series.json` | CME prediction |

---

## Explicitly Deferred from Phase 1

| Endpoint | Reason |
| --- | --- |
| `boulder_k_index_1m.json` | Local measurement |
| `predicted_fredericksburg_a_index.json` | Station-specific |
| `rtsw_ephemerides_1h.json` | Spacecraft position data |
| `electron_fluence_forecast.json` | Satellite-oriented |
| `icao-space-weather-advisories.json` | Aviation-oriented |
| `netcdf/geoelectric` | Power-grid focused |

---

## Rate Limits

No formal per-endpoint rate limits were identified during Story 3.1 research.

Radio Atlas will therefore use conservative polling intervals and avoid
requesting data more frequently than the underlying source cadence.

This assumption should be revisited if NOAA publishes explicit service
limits or usage guidance.

---

## Implementation Notes for Story 3.2

Create these models:

- `SolarFlux`
- `KpIndex`
- `SunspotNumber`
- `AuroraForecast`
- `AuroraGridCell`
- `SolarMagneticField`
- `SolarWind`

---

## Implementation Notes for Story 3.3

Implement `NOAAProvider` using:

- `httpx`
- Retry handling
- Timeout handling
- Response validation
- Structured logging

