# Analytics Aggregation Schema

## Purpose

Phase 3 introduces precomputed analytics rollups over the raw radio observation
history collected in `spots`.

The aggregation layer exists to support statistics, timeline, replay, and
anomaly-detection workloads without repeatedly scanning the complete raw
observation history.

Raw observations remain the source of truth.

## Design Principles

- Raw `spots` remain immutable analytical source data.
- Rollups are derived data and can be rebuilt from raw observations.
- Time buckets use UTC.
- Hourly rollups provide the primary analytical resolution.
- Daily rollups provide efficient long-range queries.
- Band and station dimensions are represented explicitly.
- Aggregate rows must be safe to recompute and upsert.
- Missing SNR values contribute to observation counts but not SNR statistics.
- Sender and receiver station activity are tracked independently.
- Schema design must support incremental refresh and historical backfill.
- Operating mode is preserved as an analytical dimension because activity
  patterns can differ substantially by mode.
- Geographic dimensions are not included in Phase 3 rollups. Replay and
  geographic visualization retain full location fidelity by retrieving raw
  observations; geographic aggregation can be introduced later if a concrete
  analytical query requires it.

## Hourly Band Rollups

Table: `analytics_band_hourly`

One row represents one UTC hour and band.

Fields:

| Field | Type | Purpose |
| --- | --- | --- |
| `id` | bigint | Primary key |
| `bucket_start` | timestamptz | Beginning of UTC hour |
| `band` | varchar(20) | Amateur-radio band |
| `mode` | varchar(32) | Operating mode |
| `observation_count` | bigint | Number of observations |
| `unique_sender_count` | bigint | Distinct sending stations |
| `unique_receiver_count` | bigint | Distinct receiving stations |
| `snr_sample_count` | bigint | Observations containing SNR |
| `snr_min_db` | integer nullable | Minimum observed SNR |
| `snr_max_db` | integer nullable | Maximum observed SNR |
| `snr_avg_db` | double precision nullable | Mean observed SNR |
| `created_at` | timestamptz | Row creation time |
| `updated_at` | timestamptz | Last recomputation time |

Unique key:

`(bucket_start, band, mode)`

Primary query patterns:

- activity for a band over time
- comparison of activity between bands
- signal-quality trends
- band-opening analysis
- timeline density generation
- activity for a band and mode over time
- comparison of activity between modes

## Daily Band Rollups

Table: `analytics_band_daily`

One row represents one UTC day and band.

Fields:

| Field | Type | Purpose |
| --- | --- | --- |
| `id` | bigint | Primary key |
| `bucket_start` | timestamptz | Beginning of UTC day |
| `band` | varchar(20) | Amateur-radio band |
| `mode` | varchar(32) | Operating mode |
| `observation_count` | bigint | Number of observations |
| `unique_sender_count` | bigint | Distinct sending stations |
| `unique_receiver_count` | bigint | Distinct receiving stations |
| `snr_sample_count` | bigint | Observations containing SNR |
| `snr_min_db` | integer nullable | Minimum observed SNR |
| `snr_max_db` | integer nullable | Maximum observed SNR |
| `snr_avg_db` | double precision nullable | Mean observed SNR |
| `created_at` | timestamptz | Row creation time |
| `updated_at` | timestamptz | Last recomputation time |

Unique key:

`(bucket_start, band, mode)`

Daily rollups are intended primarily for longer-range statistics where hourly
resolution would produce unnecessary query volume.

## Hourly Station Rollups

Table: `analytics_station_hourly`

One row represents one UTC hour, station, and activity direction.

Fields:

| Field | Type | Purpose |
| --- | --- | --- |
| `id` | bigint | Primary key |
| `bucket_start` | timestamptz | Beginning of UTC hour |
| `station_id` | bigint nullable | Station foreign key when available |
| `callsign` | varchar(32) | Callsign represented by the aggregate |
| `direction` | varchar(8) | `sender` or `receiver` |
| `observation_count` | bigint | Number of observations |
| `unique_counterparty_count` | bigint | Distinct stations heard or hearing |
| `snr_sample_count` | bigint | Observations containing SNR |
| `snr_min_db` | integer nullable | Minimum observed SNR |
| `snr_max_db` | integer nullable | Maximum observed SNR |
| `snr_avg_db` | double precision nullable | Mean observed SNR |
| `created_at` | timestamptz | Row creation time |
| `updated_at` | timestamptz | Last recomputation time |

Unique key:

`(bucket_start, callsign, direction)`

The callsign remains part of the analytical identity because historical raw
observations may not always contain a populated station foreign key.

Primary query patterns:

- station activity over time
- sender versus receiver activity
- station activity baselines
- anomaly detection
- station statistics

## Daily Station Rollups

Table: `analytics_station_daily`

The daily station table has the same analytical dimensions and measures as
`analytics_station_hourly`, with `bucket_start` representing the beginning of
a UTC day.

Unique key:

`(bucket_start, callsign, direction)`

This table supports long-range station statistics and baseline calculations.

## Solar Conditions

Phase 3 does not initially duplicate `solar_conditions` into a separate
analytics rollup.

The existing table already represents timestamped observations by
`observation_type` and has indexes supporting time- and type-based queries.

Statistics services can align solar observations with radio-activity buckets
by time when computing solar-condition correlations.

A dedicated solar rollup should be introduced later only if profiling shows
that correlation queries require it.

## Index Strategy

Each rollup table should index its primary time dimension.

Band rollups should support:

- `bucket_start`
- `(band, mode, bucket_start)`

Station rollups should support:

- `bucket_start`
- `(callsign, bucket_start)`
- `(station_id, bucket_start)` where a station ID exists

Unique constraints used for aggregation upserts also provide indexes for their
dimension combinations.

## Aggregation Semantics

Hourly buckets are aligned to UTC hour boundaries:

`YYYY-MM-DD HH:00:00+00`

Daily buckets are aligned to UTC midnight:

`YYYY-MM-DD 00:00:00+00`

For SNR statistics:

- observations with `snr_db IS NULL` remain part of `observation_count`
- null SNR values do not contribute to minimum, maximum, average, or
  `snr_sample_count`

For station statistics:

- each observation contributes once to the sender aggregate
- each observation contributes once to the receiver aggregate
- counterpart counts use the opposite callsign

## Rollup Derivation

Hourly and daily rollups are independently derived from raw `spots`.

Daily rollups must not be produced by simply summing hourly rollups because
distinct-count measures are not additive across time buckets. A station that
appears in multiple hourly buckets must still contribute only once to the
corresponding daily distinct count.

Accordingly:

- hourly rollups are computed from raw observations within each UTC hour
- daily rollups are computed from raw observations within each UTC day
- observation and SNR sample counts are additive, but daily jobs still derive
  them from the same raw daily source window for consistency
- minimum and maximum SNR are calculated over the complete source bucket
- average SNR is calculated from raw non-null SNR samples rather than by
  averaging hourly averages
- distinct sender, receiver, and counterparty counts are calculated over the
  complete source bucket

This keeps hourly and daily aggregates mathematically correct and allows either
resolution to be rebuilt independently from the source-of-truth observations.

## Rebuild and Refresh Model

Rollups are derived from raw observations and must therefore be reproducible.

Aggregation jobs should support:

1. Historical backfill for an arbitrary time range.
2. Incremental refresh of recently completed buckets.
3. Recalculation of an existing bucket.
4. Idempotent upsert of aggregate results.

This design allows late-arriving observations to be incorporated by
recomputing affected buckets without duplicating aggregate data.

## Phase 3 Consumers

The schema is designed to support:

- band-opening statistics
- signal-quality statistics
- station-activity statistics
- solar-condition correlation
- timeline density buckets
- replay navigation
- rolling anomaly baselines
- historical anomaly analysis

Raw observation retrieval remains available for replay frames and detailed
inspection when aggregate data does not contain sufficient resolution.
