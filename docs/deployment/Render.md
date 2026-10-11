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

The updated Blueprint runs ingestion and aggregation in a dedicated single worker and disables them inside the API. Keep one worker instance until distributed scheduling coordination exists. See Ingestion_4_6.md for cutover instructions. Rolling deploys can briefly overlap instances; monitor ingestion and idempotent rollups. Review storage growth and retention as data accumulates.

Historical globe frame integration remains separate Story 6.1 work. Deploying the timeline does not provide it.

## Verification

Run the existing frontend Docker harness. For backend checks, use the disposable database Compose project with an existing environment file containing POSTGRES_USER and POSTGRES_PASSWORD:

```sh
docker compose --env-file backend/.env -p radio-atlas-render-check -f docker-compose.replay-tests.yml run --build --rm tests /bin/sh -ec 'ruff format --check app/config.py app/main.py tests/unit/test_deployment_config.py && ruff check app/config.py app/main.py tests/unit/test_deployment_config.py && mypy && alembic upgrade head && pytest tests/unit/test_deployment_config.py tests/unit/api/test_app.py tests/unit/analytics/aggregation/test_runtime.py tests/unit/ingestion/test_runtime.py'
```

Validate render.yaml in Render's Blueprint preview before creation. No resources have been provisioned from the assistant session; account access and Docker socket access are unavailable.

References: https://render.com/docs/blueprint-spec and https://render.com/docs/deploys.
