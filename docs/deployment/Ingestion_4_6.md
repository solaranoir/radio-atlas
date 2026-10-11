# Story 4.6: Ingestion throughput cleanup

Observed production evidence: MQTT warns that its incoming queue is full and discards messages. API health responses continue. Code inspection identified sequential per-spot commits, a provider lookup per spot, blocking synchronous writes in the API event loop, and an erroneous MQTT receive loop inside shutdown cleanup.

## Draft implementation

- Buffer at most 100 normalized spots; flush after one second of sparse traffic and on stream termination.
- Bulk insert using one provider lookup per provider and one commit per batch. Roll back failed transactions and propagate errors without retrying an ambiguous write.
- Execute each database batch in a thread; wait for an in-flight write before releasing the session on cancellation. No concurrent use of the ingestion session.
- Bound recent deduplication to 100,000 keys instead of growing for the lifetime of the worker. Older duplicates may be accepted after eviction; no new database uniqueness guarantee is added.
- Remove the second MQTT subscription/receive loop from cleanup.
- Disable production ingestion and aggregation inside API replicas. A new single Render worker runs both, with signal-based shutdown and TaskGroup error propagation.

## Deployment sequence

This Blueprint adds a paid worker. Review its displayed cost before syncing. Ensure API migrations have completed before starting the worker. Deploy the updated API with RADIO_ATLAS_INGESTION_ENABLED=false and RADIO_ATLAS_AGGREGATION_ENABLED=false, then start the worker. Check it receives MQTT messages and emits batch-persisted logs. Avoid overlapping old embedded ingestion and the worker during cutover; short collection gaps during manual cutover are possible.

The API's provider health is process-local and no longer represents the dedicated worker. Use worker logs to inspect ingestion. Persistent backlog/drop metrics and durable queueing remain follow-ups. Bounded queues can still drop reports if sustained input exceeds batch throughput. This draft does not claim a measured production throughput improvement.

## Verification

```sh
docker compose --env-file backend/.env -p radio-atlas-story46 -f docker-compose.replay-tests.yml run --build --rm tests /bin/sh -ec 'ruff format --check app tests && ruff check app tests && mypy && alembic upgrade head && pytest tests/unit/ingestion tests/unit/test_psk_reporter_provider.py tests/unit/test_observation_deduplication.py tests/unit/analytics/aggregation tests/integration/test_psk_reporter_integration.py --cov=app.ingestion.psk_reporter --cov-report=term-missing --cov-fail-under=85'
```

Current evidence: formatting and Ruff checks pass on changed Python files; focused mypy passes. Docker socket access is denied in the assistant session, so runtime regression/coverage and load verification are pending. Before merging, confirm real PostgreSQL bulk persistence and repeat production observations of batch duration, queue warnings, API latency, memory, and graceful worker shutdown.
