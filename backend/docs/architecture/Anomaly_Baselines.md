# Anomaly Baselines (Phase 3 Story 5.2)

This document records what Story 5.2 built: robust, seasonal baselines that describe
normal behavior for each band/mode and for the busiest stations. Story 5.3 scores
anomalies against them. The design and its reasoning are in `Anomaly_Detection.md`
(sections 4.3, 4.4, 6.2, 6.3 and 9.1).

## What a baseline is

A baseline snapshot answers this question for one dimension, metric and seasonal slot:
what is normal, using only data from before `as_of`?

| Field | Meaning |
| --- | --- |
| `dimension_type` / `dimension_key` | `band` (`band=20m\|mode=FT8`) or `station` (`callsign=K1ABC\|direction=receiver`) |
| `metric` | Band: `observation_count`, `unique_sender_count`, `unique_receiver_count`, `snr_avg_db`. Station: `observation_count`, `unique_counterparty_count`, `snr_avg_db` |
| `resolution` / `slot` | `hour` with UTC hour 0–23, or `day` with ISO weekday 1–7 |
| `center` / `scale` / `mad` | Cohort median, the scale used for scoring (`max(MAD, floor)`), and the raw MAD. All are in model space |
| `transform` | `log1p` for counts, `identity` for SNR |
| `expected_value` | `center` converted back to natural units, for display |
| `method` | `seasonal_median_mad`, `fallback_recent_median_mad` or `none` |
| `quality` | `sufficient`, `sparse`, `degenerate` or `insufficient` (see below) |
| `sample_count`, `cohort_start`, `cohort_end` | The cohort the numbers came from |
| `baseline_version` | Config label plus a fingerprint of every parameter |

Story 5.3 computes the robust Z-score as
`0.6745 * (to_model_space(actual) - center) / scale`.

## Cohorts

| Resolution | Seasonal cohort (preferred) | Fallback |
| --- | --- | --- |
| hour | Same UTC hour on earlier days within 28 days. Needs at least 8 samples. | All hourly buckets in the last 7 days. Needs at least 24. |
| day | Same weekday on earlier weeks within 12 weeks. Needs at least 4 samples. | All daily buckets in the last 28 days. Needs at least 7. |

Rules that keep baselines honest:

- **No future data.** Only buckets that start strictly before `as_of` are used. The
  pure function enforces this whatever the caller passes in, and so does the database
  query.
- **Ingestion gaps are not silence.** Count metrics are zero-filled only for buckets in
  which some band rollup exists, meaning ingestion was running. Buckets with no data
  anywhere stay absent. SNR is never zero-filled.
- **Thin SNR averages are dropped.** An SNR bucket built from fewer than 5 samples
  counts as missing.

## Quality

The first matching rule wins:

1. `insufficient`: neither cohort reached its minimum size. There is no center or
   scale.
2. `sparse`: the fallback cohort was used, or the expected value is below the metric's
   activity guard (3 spots, or 2 distinct stations). This is the sparse-series guard
   that Story 5.1 asked for: a one-spot burst on a quiet band must not become an
   alert.
3. `degenerate`: the cohort has no spread (MAD = 0). Scoring uses the configured
   floor.
4. `sufficient`: everything else.

`BaselineSnapshot.is_usable` is true for `sufficient` and `degenerate`. Story 5.3
should not raise alerts against `sparse` or `insufficient` baselines.

## Versioning

`BaselineConfig.version` is `"<label>.<sha256 of all parameters>[:10]"`, for example
`seasonal-mad-v1.fc90487206`. Changing any window, minimum, floor, guard or station
limit produces a new version. Stored snapshots and future anomaly events therefore
always name the exact configuration they came from.

## Storage (bounded)

`anomaly_baselines` holds only the **current** snapshot for each (version, dimension,
metric, resolution, slot). Each refresh deletes the version's rows and inserts the new
set in one transaction. It then prunes rows belonging to other versions.

Size with the default config and the current five-band ingestion:

- Bands: about 15 band/mode series × 31 slots × 4 metrics ≈ 1,900 rows.
- Stations: capped at the 500 busiest callsign/direction pairs from the last 7 days of
  daily rollups. That is 500 × 31 × 3 ≈ 46,500 rows, roughly 15–20 MB including the
  unique index.

Historical baselines are not stored. A baseline for any past `as_of` can be recomputed
exactly from the rollups, which are kept forever. Story 5.3 should copy the
center, scale, sample count and version it scored against into each anomaly's evidence
record (`Anomaly_Detection.md` section 9).

## Running it

- **Worker:** when `RADIO_ATLAS_BASELINES_ENABLED=true`, the worker refreshes
  baselines right after each daily rollup refresh, with `as_of` set to the start of the
  current UTC day. A failure is logged as `Baseline refresh failed` and retried on the
  next day. It never stops ingestion. A success logs `Baselines refreshed` with
  snapshot and quality counts.
- **Backfill or coverage check:**

  ```sh
  # Read-only dry run with a coverage table
  python -m app.analytics.anomalies.baselines_cli --as-of 2026-11-20
  # Store as the current set
  python -m app.analytics.anomalies.baselines_cli --as-of 2026-11-20 --write
  # Bands only, for roles without SELECT on the station rollup tables
  python -m app.analytics.anomalies.baselines_cli --no-stations
  ```

## Code map

| Module | Role |
| --- | --- |
| `app/analytics/anomalies/robust.py` | Median, MAD and modified Z. Shared with the Story 5.1 harness |
| `app/analytics/anomalies/config.py` | `BaselineConfig`, `MetricSpec`, `CohortSpec`, the default config and its version |
| `app/analytics/anomalies/models.py` | `DimensionKey`, `RollupValue`, `BaselineSnapshot`, method and quality enums |
| `app/analytics/anomalies/baseline.py` | Pure series building, cohort selection and snapshot computation |
| `app/analytics/anomalies/queries.py` | Rollup reads: active buckets, band rows, top stations, station rows |
| `app/analytics/anomalies/persistence.py` | Replace-per-version, pruning and coverage reads |
| `app/analytics/anomalies/service.py` | `compute_baselines` (read-only, any `as_of`) and `refresh_baselines` |
| `app/analytics/anomalies/runtime.py` | Daily worker step |
| `app/analytics/anomalies/baselines_cli.py` | Backfill and coverage CLI |

## Known limits

- Daily baselines use the daily rollups. The daily rollup job runs every 24 hours from
  worker start, not at midnight, so the refresh runs right after it to pick up
  yesterday's rollup.
- Stations outside the top 500 have no stored baseline. `compute_baselines` can still
  produce one on demand if Story 5.3 needs it.
- Defaults are starting points from the Story 5.1 synthetic evaluation. They should be
  re-checked when the historical run (`Anomaly_Detection.md` section 8.4) has real
  data.
