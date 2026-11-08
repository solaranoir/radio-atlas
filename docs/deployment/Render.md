# Deploy Radio Atlas on Render

The root render.yaml defines a static frontend, Docker API, Postgres, and Key Value cache. API, database, and cache use paid plans in Oregon; review the total price shown by Render before creating resources.

## First deployment

1. Merge Story 4.4 and these deployment changes into main after Docker verification.
2. In Render, select New > Blueprint, authorize GitHub access to solaranoir/radio-atlas, select main, and use render.yaml.
3. Supply VITE_API_BASE_URL as the API's public HTTPS URL (no trailing slash or /api/v1). Supply RADIO_ATLAS_CORS_ORIGINS as a JSON array containing the frontend's exact HTTPS origin, for example ["https://your-frontend.onrender.com"]. If assigned URLs are not known during creation, update both environment values after creation and redeploy frontend and API. Do not assume service names equal assigned hostnames.
4. Review resources and prices, then create the Blueprint. Database/cache connection strings are populated internally; do not copy secrets into source code.
5. Confirm migrations complete before API startup. The startup command binds to Render's PORT; local Compose still runs migrations automatically and defaults to port 8000.
6. Confirm /health responds, both external providers ingest, and aggregation jobs run. Check logs after at least one scheduling interval. The existing /health endpoint returns 200 even for unhealthy providers: inspect its JSON and logs too.
7. Open the frontend, validate timeline data and seek/play/pause, and check the browser Network panel for a secure WebSocket connection. Verify reconnection after an API redeploy.

A new database contains no local history. Let ingestion accumulate observations or perform a separately planned import and rollup backfill. Never point cloud services at the development database.

## Runtime constraints

The updated Blueprint runs ingestion and aggregation in a dedicated single worker and disables them inside the API. Keep one worker instance until distributed scheduling coordination exists. See Ingestion_4_6.md for cutover instructions. Rolling deploys can briefly overlap instances; monitor ingestion and idempotent rollups. Review storage growth as data accumulates.

## Spot retention and MQTT topics

The worker deletes raw spots older than `RADIO_ATLAS_SPOT_RETENTION_DAYS` (application default 14; render.yaml sets 3; 0 disables; minimum 3). Retention runs 5 minutes after the worker starts and then hourly. Each expired UTC day is processed oldest-first. The day's hourly and daily rollups are rebuilt from its raw spots and the day is recorded in `spot_retention_days` in one transaction, then its spots are deleted in 10,000-row committed batches. Rollups are kept indefinitely, so analytics, the timeline and anomaly detection keep their full history. Raw-spot replay covers only the retention window.

Rebuilding a day before deleting it also repairs hours a failed aggregation run missed. The first run after enabling retention can take a long time on a large backlog: it runs in a background thread and resumes where it stopped after a restart. Deleted rows free space for reuse inside Postgres, so the disk stops growing but does not shrink.

Size the retention window and disk together. The job keeps N full UTC days plus the current day, so peak raw storage is about (N + 1) x daily volume. At the 219 spots/s sampled below, and the earlier estimate of 270 bytes per spot, daily volume is about 5.1 GB. That estimate predates the removal of five unused `spots` indexes, so measure the real figure with `pg_total_relation_size('spots')`. 20m FT8 alone peaked at about 540,000 spots per hour.

If the disk fills, Render suspends the database. Suspend the worker, resume the database, and raise its storage straight away. Storage cannot be reduced later. Keep `diskSizeGB` in render.yaml in step with the dashboard value.

`PSK_REPORTER_MQTT_TOPICS` takes a JSON array of topics, for example `["pskr/filter/v2/+/FT8/#","pskr/filter/v2/+/FT4/#"]` for FT8 and FT4 on all bands. The default remains `["pskr/filter/v2/20m/FT8/#"]`. A 2-minute sample at 03:17 UTC on 2026-11-05 measured about 219 spots/s across all bands and modes, 205/s of them FT8. Check database CPU, insert latency and MQTT queue warnings before widening the topics on the current plans.

## Known storage and history limitations

The production settings of 3 retention days and a 30 GB disk follow a database suspension in November 2026. All-band ingestion was writing an estimated 5.1 GB/day to a 15 GB disk, so the disk could fill before the 14-day window deleted anything.

- **Raw history is short.** Replay and minute-resolution timeline data cover only the retained raw spots: 3 full UTC days plus the current day. Hourly and daily rollups are kept, but they have no geographic or per-spot detail and cannot rebuild replay.
- **Expired replay ranges are not rejected.** Creating a replay session does not check the range against retained data, so a session for an expired range returns no observations and no error. The timeline's history bounds extend back to the earliest rollup, so they can include times that replay cannot show.
- **Zero does not always mean no activity.** Minute-resolution timeline buckets older than the raw window count as zero. Downtime gaps also look like quiet periods.
- **Outages leave permanent gaps.** The worker reads a live MQTT feed and does not backfill, so spots published while it is stopped are not recovered.
- **Nothing stops the disk filling.** No code limits database size or pauses ingestion as the disk fills. Raising the ingestion rate or retention days without raising storage can cause another suspension. Storage autoscaling is available as a backstop, but each increase is permanent.
- **Capacity figures are estimates.** The ingestion rate comes from one 2-minute sample, and 270 bytes per spot was not measured after the unused indexes were removed. Check real disk use for several days after changing either.
- **Rollups grow indefinitely.** Hourly station rollups add one row per callsign, direction and hour and are never deleted. Their long-term size has not been measured, so include them in disk reviews.

Longer raw history needs more storage. Time-partitioning `spots` could make deletion cheaper, but it is not implemented and would not reduce the storage a given window needs.

Historical globe frame integration remains separate Story 6.1 work. Deploying the timeline does not provide it.

## Verification

Run the existing frontend Docker harness. For backend checks, use the disposable database Compose project with an existing environment file containing POSTGRES_USER and POSTGRES_PASSWORD:

```sh
docker compose --env-file backend/.env -p radio-atlas-render-check -f docker-compose.replay-tests.yml run --build --rm tests /bin/sh -ec 'ruff format --check app/config.py app/main.py tests/unit/test_deployment_config.py && ruff check app/config.py app/main.py tests/unit/test_deployment_config.py && mypy && alembic upgrade head && pytest tests/unit/test_deployment_config.py tests/unit/api/test_app.py tests/unit/analytics/aggregation/test_runtime.py tests/unit/ingestion/test_runtime.py'
```

Validate render.yaml in Render's Blueprint preview before creation. No resources have been provisioned from the assistant session; account access and Docker socket access are unavailable.

References: https://render.com/docs/blueprint-spec and https://render.com/docs/deploys.
