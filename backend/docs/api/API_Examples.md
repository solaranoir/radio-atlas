# Radio Atlas API Examples

The Radio Atlas API exposes normalized radio observations, solar conditions,
and station information under `/api/v1`.

The examples below show common requests, filtering and pagination patterns,
representative response payloads, and standardized API errors.

## Observations

`GET /api/v1/observations` returns normalized PSK Reporter spot observations.
Results are ordered newest-first and may be filtered by time range and
amateur-radio band.

### Observations basic request

```http
GET /api/v1/observations
```

### Observations filtered by band

```http
GET /api/v1/observations?band=20m
```

### Observations filtered by time range

```http
GET /api/v1/observations?start_time=2026-08-20T00:00:00Z&end_time=2026-08-21T00:00:00Z
```

`start_time` and `end_time` use ISO 8601 UTC timestamps. The time range is
inclusive, and `start_time` must be before or equal to `end_time`.

### Observations with combined filters

```http
GET /api/v1/observations?band=20m&start_time=2026-08-20T00:00:00Z&end_time=2026-08-21T00:00:00Z
```

### Observations pagination

```http
GET /api/v1/observations?limit=50&offset=100
```

`limit` defaults to `100` and must be between `1` and `500`. `offset` defaults
to `0` and must be zero or greater.

### Observations example response

```json
[
  {
    "id": 42,
    "provider_id": 2,
    "sequence_number": 71899472730,
    "sender_callsign": "EA5JLN",
    "receiver_callsign": "DL4JC",
    "sender_grid": "IM99TN",
    "receiver_grid": "JN39LH",
    "frequency_hz": 14075361,
    "band": "20m",
    "mode": "FT8",
    "snr_db": -5,
    "observed_at": "2026-08-20T20:35:44Z",
    "transmitted_at": "2026-08-20T20:35:29Z"
  }
]
```

## Solar Conditions

`GET /api/v1/solar-conditions` returns normalized NOAA space-weather
observations. Results are ordered newest-first and may be filtered by
observation type or time range.

### Solar conditions basic request

```http
GET /api/v1/solar-conditions
```

### Solar conditions filtered by observation type

```http
GET /api/v1/solar-conditions?observation_type=solar_wind
```

Normalized observation types may include `solar_flux`, `kp_index`,
`sunspot_number`, `aurora`, `magnetic_field`, and `solar_wind`.

### Solar conditions filtered by time range

```http
GET /api/v1/solar-conditions?start_time=2026-08-20T00:00:00Z&end_time=2026-08-21T00:00:00Z
```

`start_time` and `end_time` use ISO 8601 UTC timestamps. The time range is
inclusive, and `start_time` must be before or equal to `end_time`.

### Solar conditions with combined filters

```http
GET /api/v1/solar-conditions?observation_type=solar_wind&start_time=2026-08-20T00:00:00Z&end_time=2026-08-21T00:00:00Z
```

### Solar conditions pagination

```http
GET /api/v1/solar-conditions?limit=50&offset=100
```

`limit` defaults to `100` and must be between `1` and `500`. `offset` defaults
to `0` and must be zero or greater.

### Solar conditions example response

```json
[
  {
    "id": 17,
    "provider_id": 1,
    "observation_type": "solar_wind",
    "observed_at": "2026-08-20T12:00:00Z",
    "value": 432.5,
    "unit": "km/s",
    "data": {
      "density": 6.2,
      "temperature": 118000,
      "source": "ACE"
    }
  }
]
```

## Stations

`GET /api/v1/stations` returns stations observed in normalized radio spot data.
Results are ordered by callsign ascending.

### Stations basic request

```http
GET /api/v1/stations
```

### Stations filtered by callsign

```http
GET /api/v1/stations?callsign=KK7QEA
```

Callsign matching is case-insensitive and callsigns are normalized to uppercase
for querying. Lowercase input is also valid:

```http
GET /api/v1/stations?callsign=kk7qea
```

### Stations pagination

```http
GET /api/v1/stations?limit=50&offset=100
```

`limit` defaults to `100` and must be between `1` and `500`. `offset` defaults
to `0` and must be zero or greater.

### Stations example response

```json
[
  {
    "id": 42,
    "callsign": "KK7QEA",
    "grid_square": "DM25",
    "latitude": 36.0395,
    "longitude": -114.9817,
    "entity_id": 291,
    "first_seen_at": "2026-08-20T12:00:00Z",
    "last_seen_at": "2026-08-24T17:30:00Z"
  }
]
```

## Error Examples

API errors use a consistent JSON error envelope containing an error code,
a human-readable message, and additional details when applicable.

### Invalid time range error

A `400 Bad Request` is returned when individually valid time parameters form
an invalid range because `start_time` is later than `end_time`.

```http
GET /api/v1/observations?start_time=2026-08-21T00:00:00Z&end_time=2026-08-20T00:00:00Z
```

```json
{
  "error": {
    "code": "invalid_time_range",
    "message": "start_time must be before or equal to end_time"
  }
}
```

The same time-range validation applies to `/api/v1/solar-conditions`.

### Request validation error

A `422 Unprocessable Entity` is returned when a query parameter fails request
validation.

For example, `limit` must be at least `1`:

```http
GET /api/v1/observations?limit=0
```

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed",
    "details": [
      {
        "type": "greater_than_equal",
        "loc": [
          "query",
          "limit"
        ],
        "msg": "Input should be greater than or equal to 1"
      }
    ]
  }
}
```

Other requests that produce `422` validation errors include:

```http
GET /api/v1/observations?limit=501
GET /api/v1/observations?offset=-1
GET /api/v1/observations?start_time=not-a-date
GET /api/v1/solar-conditions?limit=0
GET /api/v1/solar-conditions?offset=-1
GET /api/v1/stations?limit=501
GET /api/v1/stations?offset=-1
```

### Response validation error

A `500 Internal Server Error` is returned when internal data cannot be
serialized into an endpoint's declared response model.

```json
{
  "error": {
    "code": "response_validation_error",
    "message": "Response validation failed"
  }
}
```

A response-validation error indicates an internal API or data-contract problem
rather than an invalid client request.

## Query Parameter Reference

### Observations query parameters

| Parameter | Example | Description |
| --- | --- | --- |
| `start_time` | `2026-08-20T00:00:00Z` | Records at or after this UTC timestamp |
| `end_time` | `2026-08-21T00:00:00Z` | Records at or before this UTC timestamp |
| `band` | `20m` | Filter by amateur-radio band |
| `limit` | `100` | Maximum results, from 1 through 500 |
| `offset` | `0` | Number of results to skip |

### Solar conditions query parameters

| Parameter | Example | Description |
| --- | --- | --- |
| `observation_type` | `solar_wind` | Filter by normalized observation type |
| `start_time` | `2026-08-20T00:00:00Z` | Records at or after this UTC timestamp |
| `end_time` | `2026-08-21T00:00:00Z` | Records at or before this UTC timestamp |
| `limit` | `100` | Maximum results, from 1 through 500 |
| `offset` | `0` | Number of results to skip |

### Stations query parameters

| Parameter | Example | Description |
| --- | --- | --- |
| `callsign` | `KK7QEA` | Filter by callsign; matching is case-insensitive |
| `limit` | `100` | Maximum results, from 1 through 500 |
| `offset` | `0` | Number of results to skip |

## Interactive API Documentation

When the Radio Atlas API is running locally, FastAPI exposes the generated
OpenAPI schema at:

```text
/openapi.json
```

Interactive Swagger documentation is available at:

```text
/docs
```

The generated documentation includes endpoint descriptions, query-parameter
descriptions and examples, response schemas, representative payload examples,
and standardized error responses.
