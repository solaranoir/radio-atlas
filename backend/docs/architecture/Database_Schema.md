# Radio Atlas Database Schema

## Design Goals

The Phase 1 database schema is designed to:

- preserve provenance for all externally sourced observations;
- support normalized NOAA and PSK Reporter data;
- preserve historical spot data independently of later station updates;
- support time-based and band-based API queries;
- support duplicate detection and database-level uniqueness rules;
- use PostgreSQL-native data types where appropriate;
- remain extensible for future providers and observation types.

PostgreSQL is the Phase 1 system of record.

## Entity Overview

| Entity | Purpose |
|---|---|
| `providers` | Registry of external data providers |
| `users` | Radio Atlas application accounts |
| `stations` | Amateur-radio stations observed by the platform |
| `spots` | PSK Reporter reception observations |
| `solar_conditions` | Normalized NOAA solar and space-weather observations |

## Providers

The `providers` table records the external source responsible for
an observation. Provider identity is stored separately from individual
observations so provenance can be queried consistently.

```text
providers
---------
id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY
name            VARCHAR(100) NOT NULL UNIQUE
display_name    VARCHAR(255) NOT NULL
provider_type   VARCHAR(50) NOT NULL
enabled         BOOLEAN NOT NULL DEFAULT TRUE
created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
updated_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
```

Initial provider records:

| Name | Display Name | Type |
|---|---|---|
| `noaa` | NOAA Space Weather Prediction Center | `solar` |
| `psk_reporter` | PSK Reporter | `spot` |

## Users

The `users` table represents Radio Atlas application accounts.

Users are distinct from observed amateur-radio stations. A station may
exist in Radio Atlas without any associated user account, and Phase 1
does not require a user-to-station relationship.

```text
users
-----
id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY
email           VARCHAR(320) NOT NULL UNIQUE
callsign        VARCHAR(32)
created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
updated_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
```
Design decision is not to constrain users to one account per callsign at this time.

## Stations

A station represents an amateur-radio station observed by Radio Atlas.

The callsign is the canonical station identifier for Phase 1.
Grid square and coordinates represent the most recently known station
location and may change over time.

Historical location information remains preserved on individual spot
records.

```text
stations
--------
id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY
callsign        VARCHAR(32) NOT NULL UNIQUE
grid_square     VARCHAR(10)
latitude        DOUBLE PRECISION
longitude       DOUBLE PRECISION
entity_id       INTEGER
first_seen_at   TIMESTAMPTZ
last_seen_at    TIMESTAMPTZ
created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
updated_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
```

## Spots

The `spots` table stores normalized radio reception observations from
PSK Reporter.

Calls/call grids are retained directly on each spot as a historical
snapshot even when the corresponding station record changes later.

```text
spots
-----
id                    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY
provider_id           BIGINT NOT NULL
sequence_number       BIGINT
sender_station_id     BIGINT
receiver_station_id   BIGINT
sender_callsign       VARCHAR(32) NOT NULL
receiver_callsign     VARCHAR(32) NOT NULL
sender_grid           VARCHAR(10)
receiver_grid         VARCHAR(10)
frequency_hz          BIGINT
band                  VARCHAR(20)
mode                  VARCHAR(32) NOT NULL
snr_db                INTEGER
observed_at           TIMESTAMPTZ NOT NULL
transmitted_at        TIMESTAMPTZ
sender_entity_id      INTEGER
receiver_entity_id    INTEGER
created_at            TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
```

Station foreign keys are nullable because a spot can be persisted even
if station enrichment or station-record creation has not yet completed.
The callsign and grid values on the spot remain the authoritative
observation-time snapshot.

Foreign-key relationships:

- `provider_id` → `providers.id`
- `sender_station_id` → `stations.id`
- `receiver_station_id` → `stations.id`

## Solar Conditions

```text
solar_conditions
----------------
id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY
provider_id         BIGINT NOT NULL
observation_type    VARCHAR(50) NOT NULL
observed_at         TIMESTAMPTZ NOT NULL
value               DOUBLE PRECISION
unit                VARCHAR(32)
data                JSONB NOT NULL DEFAULT '{}'::jsonb
created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
```
Table stores normalized NOAA observations and uses JSONB for feed-specific detail.

Foreign-key relationships:

- `provider_id` → `providers.id`

## Relationships

```text
providers 1 ────── * spots

providers 1 ────── * solar_conditions

stations 1 ─────── * spots
         sender_station_id

stations 1 ─────── * spots
         receiver_station_id   
```

## Observation Uniqueness Rules

### PSK Reporter Spots

When a PSK Reporter sequence number is available, the canonical
upstream identity is:

`provider_id + sequence_number`

For spots without a sequence number, the fallback application-level
identity is:

- provider
- observed timestamp
- sender callsign
- receiver callsign
- frequency
- mode

### Solar Conditions

Solar observations are uniquely identified by:

- provider
- observation type
- observed timestamp

Conceptually:

`provider_id + observation_type + observed_at`

This prevents duplicate ingestion of the same NOAA observation while
allowing multiple observation types at the same timestamp.

## Data Type Decisions

### Primary Keys

`BIGINT GENERATED ALWAYS AS IDENTITY` is used for internal surrogate
primary keys.

### Timestamps

All persisted observation timestamps use PostgreSQL `TIMESTAMPTZ`.

Radio Atlas domain timestamps are timezone-aware, and PostgreSQL should
preserve that contract.

### Frequencies

Radio frequencies are stored as integer Hz using `BIGINT`.

This preserves the original PSK Reporter precision and avoids
floating-point rounding.

### Coordinates

Latitude and longitude use `DOUBLE PRECISION`.

Domain validation restricts latitude to -90 through 90 and longitude
to -180 through 180.

### Flexible Solar Data

`solar_conditions.data` uses `JSONB` for observation-specific NOAA
fields that do not justify dedicated columns in Phase 1.

Examples include:

- estimated Kp metadata;
- solar-wind density and temperature;
- magnetic-field values;
- aurora forecast metadata and grid cells.

Frequently queried fields remain first-class columns rather than being
hidden inside JSONB.

## Phase 1 Boundaries

Story 6.1 defines the logical schema only.

The following are intentionally deferred:

- ERD generation → Story 6.2
- physical indexes → Story 6.3
- Alembic migrations → Story 6.3
- rollback procedures → Story 6.3
- database integration tests → Story 6.4
- authentication schema expansion → future work

The schema is designed to support the Phase 1 observation APIs,
including time filtering, pagination, band filtering, solar-condition
queries, and station queries.

## Future Considerations

Potential future extensions include:

- user-to-station associations;
- station location history;
- additional external providers;
- propagation-derived observations;
- partitioning high-volume spot data by time;
- archival policies;
- HTTP/MQTT ingestion provenance details;
- richer authentication and authorization models.






