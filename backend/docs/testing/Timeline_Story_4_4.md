# Story 4.4: Timeline verification

Acceptance: timeline tests pass across zoom levels, marker placement, seek synchronization, and frontend interactions.

## Coverage

- Backend timeline service tests cover automatic minute/hour/day resolution with contiguous buckets, bounded counts, and exact viewport endpoints.
- Existing seeded PostgreSQL tests check raw/rollup counts and half-open boundaries at each resolution.
- Frontend component tests check marker coordinates at the beginning, midpoint, and end; proportional bar width/height; marker selection and replay cursor synchronization; zoom range round-trips without creating or seeking replay sessions.
- Existing component/hook tests cover debounced seeks, serialized requests, expired sessions, playback controls, connection state, errors, empty data, modal focus restoration, and marker pagination.

## Run from repository root

Frontend lint, build, tests, and coverage:

```sh
docker compose -p radio-atlas-story44 -f docker-compose.frontend-tests.yml run --build --rm tests
```

Backend formatting, lint, typing, timeline unit/integration tests, and coverage using a disposable PostgreSQL database (use an existing local environment file defining POSTGRES_USER and POSTGRES_PASSWORD):

```sh
docker compose --env-file backend/.env -p radio-atlas-story44-backend -f docker-compose.replay-tests.yml run --build --rm tests /bin/sh -ec 'ruff format --check app/timeline tests/unit/timeline tests/integration/timeline && ruff check app/timeline tests/unit/timeline tests/integration/timeline && mypy && alembic upgrade head && pytest tests/unit/timeline tests/unit/api/test_timeline.py tests/integration/timeline --cov=app.timeline --cov-report=term-missing --cov-fail-under=85'
```

If formatting reports changes, run `ruff format tests/unit/timeline/test_service.py` in the same container before repeating verification.

## Current evidence

New frontend tests pass TypeScript and ESLint static checks. Docker execution is blocked in the assistant session by Docker socket permissions; new runtime tests and backend formatter checks are pending. Earlier Story 4.3 passing results do not validate these additions.

Branch ph3story/4.4 starts at local main commit 1011e77 (merged Story 4.3). Fetch/pull was attempted but failed to resolve github.com; remote freshness remains unverified. Preserve the pre-existing untracked frontend Compose harness and Timeline_Frontend.md documentation.
