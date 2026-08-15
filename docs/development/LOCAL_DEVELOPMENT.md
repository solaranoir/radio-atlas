# Local Development

## Prerequisites

- Docker Desktop or Docker Engine
- Docker Compose plugin
- Git

## Initial Setup

1. Clone the repository.
2. Copy `.env.example` to `.env`.
3. Set local development values.
4. Run `docker compose up --build`.

## Local Services

| Service | URL / Port |
| --- | --- |
| FastAPI | http://localhost:8000 |
| OpenAPI UI | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

## Stop the Stack

```bash
docker compose down
```

## Reset All Local Data

```bash
docker compose down -v
```

> Warning: This permanently deletes the local PostgreSQL and Redis named volumes.

## Logs

```bash
docker compose logs -f
```

## Database Shell

```bash
docker compose exec db psql -U radio_atlas -d radio_atlas
```

## Redis Shell

```bash
docker compose exec redis redis-cli
```

## Troubleshooting

Document known local setup issues here.
