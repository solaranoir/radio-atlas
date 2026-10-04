"""Real PostgreSQL commits and production HTTP/WebSocket dependencies, without ingestion."""

import os
from collections.abc import Generator
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from time import perf_counter
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, delete, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.config import Settings
from app.infrastructure.database.models import Provider, ReplaySessionRecord, Spot
from app.main import create_app
from app.replay.session.expiry import cleanup_expired_replay_sessions
from app.replay.session.models import ReplayState
from app.replay.session.service import ReplaySessionService

START = datetime(1999, 1, 1, 10, tzinfo=UTC)
END = START + timedelta(minutes=10)
BASE = "/api/v1/replay/sessions"
pytestmark = pytest.mark.integration


@pytest.fixture
def replay_api() -> Generator[tuple[TestClient, Engine, list[str]], None, None]:
    engine = create_engine(Settings().radio_atlas_database_url)
    assert engine.url.database == "radio_atlas_replay_test", (
        "Use the disposable database from docker-compose.replay-tests.yml"
    )
    app = create_app()
    ids: list[str] = []

    def database() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    # Override only connection provisioning: services, queries and commits remain real.
    app.dependency_overrides[get_db] = database
    client = TestClient(app)
    try:
        # Do not enter TestClient's lifespan: replay tests must never ingest live providers.
        yield client, engine, ids
    finally:
        client.close()
        with engine.begin() as connection:
            connection.execute(
                delete(ReplaySessionRecord).where(ReplaySessionRecord.session_id.in_(ids))
            )
        engine.dispose()


@pytest.mark.parametrize("speed", [0.25, 1.0, 4.0, 16.0])
def test_http_lifecycle_survives_independent_database_sessions(
    replay_api: tuple[TestClient, Engine, list[str]], speed: float
) -> None:
    client, engine, ids = replay_api
    created = client.post(BASE, json={"start_time": START.isoformat(), "end_time": END.isoformat()})
    assert created.status_code == 201, created.text
    session_id = created.json()["session_id"]
    ids.append(session_id)
    path = f"{BASE}/{session_id}"
    assert created.json()["state"] == "paused"
    for action in [{"action": "play"}, {"action": "speed", "speed": speed}]:
        response = client.patch(path, json=action)
        assert response.status_code == 200, response.text
    now = datetime(2026, 10, 3, tzinfo=UTC)
    with Session(engine) as db:
        advanced = ReplaySessionService(db).advance_session(
            session_id, elapsed=timedelta(seconds=2), now=now
        )
        assert advanced is not None
    current = client.get(path)
    assert current.status_code == 200
    assert datetime.fromisoformat(current.json()["position"]) == START + timedelta(
        seconds=2 * speed
    )
    assert current.json()["speed"] == speed
    assert client.patch(path, json={"action": "pause"}).json()["state"] == "paused"
    target = START + timedelta(seconds=123, microseconds=456789)
    assert (
        client.patch(path, json={"action": "seek", "position": target.isoformat()}).status_code
        == 200
    )
    with Session(engine) as db:
        persisted = ReplaySessionService(db).get_session(session_id)
        assert persisted is not None
        assert persisted.position == target
        assert persisted.state is ReplayState.PAUSED
        assert persisted.created_at == datetime.fromisoformat(created.json()["created_at"])
    assert (
        client.patch(path, json={"action": "seek", "position": END.isoformat()}).json()["state"]
        == "completed"
    )
    assert client.patch(path, json={"action": "play"}).json()["state"] == "completed"
    assert (
        client.patch(path, json={"action": "seek", "position": START.isoformat()}).json()["state"]
        == "paused"
    )
    # Expiry is checked across a committed database session, then through HTTP.
    with Session(engine) as db:
        replay = ReplaySessionService(db).get_session(session_id)
        assert replay is not None
        deleted = cleanup_expired_replay_sessions(
            db, now=replay.updated_at + timedelta(days=2), ttl_seconds=86400
        )
        db.commit()
        assert deleted >= 1
    assert client.get(path).status_code == 404


@pytest.mark.parametrize("speed", [0.5, 1.0, 2.0])
def test_real_websocket_streams_seeded_half_open_window(
    replay_api: tuple[TestClient, Engine, list[str]], speed: float
) -> None:
    client, engine, ids = replay_api
    provider_id: int | None = None
    try:
        with Session(engine) as db:
            provider = Provider(
                name=f"replay-{uuid4()}", display_name="Replay fixture", provider_type="spot"
            )
            db.add(provider)
            db.flush()
            provider_id = provider.id
            spots = [
                Spot(
                    provider_id=provider_id,
                    sequence_number=index,
                    sender_callsign="TEST",
                    receiver_callsign="FIXTURE",
                    mode="FT8",
                    observed_at=START + timedelta(microseconds=offset * speed),
                )
                for index, offset in enumerate([0, 50_000, 100_000, 199_998, 200_000])
            ]
            db.add_all(spots)
            db.flush()
            observation_ids = [spot.id for spot in spots]
            db.commit()
        created = client.post(
            BASE,
            json={
                "start_time": START.isoformat(),
                "end_time": (START + timedelta(milliseconds=200 * speed)).isoformat(),
            },
        )
        assert created.status_code == 201, created.text
        session_id = created.json()["session_id"]
        ids.append(session_id)
        assert (
            client.patch(
                f"{BASE}/{session_id}", json={"action": "speed", "speed": speed}
            ).status_code
            == 200
        )
        assert client.patch(f"{BASE}/{session_id}", json={"action": "play"}).status_code == 200
        with (
            patch("app.api.routes.replay.REPLAY_STREAM_TICK_INTERVAL", timedelta(milliseconds=100)),
            client.websocket_connect(f"{BASE}/{session_id}/stream") as websocket,
        ):
            initial = websocket.receive_json()
            first = websocket.receive_json()
            second = websocket.receive_json()
        assert initial["type"] == "session"
        assert [item["id"] for item in first["observations"]] == observation_ids[:2]
        assert [item["id"] for item in second["observations"]] == observation_ids[2:4]
        assert datetime.fromisoformat(first["position"]) == START + timedelta(
            milliseconds=100 * speed
        )
        assert datetime.fromisoformat(second["position"]) == START + timedelta(
            milliseconds=200 * speed
        )
        assert second["state"] == "completed"
        assert client.get(f"{BASE}/{session_id}").json()["state"] == "completed"
    finally:
        if provider_id is not None:
            with engine.begin() as connection:
                connection.execute(delete(Spot).where(Spot.provider_id == provider_id))
                connection.execute(delete(Provider).where(Provider.id == provider_id))


def test_concurrent_replay_sessions_are_isolated_and_persisted(
    replay_api: tuple[TestClient, Engine, list[str]],
) -> None:
    client, engine, ids = replay_api
    count = int(os.environ.get("REPLAY_LOAD_SESSIONS", "32"))
    workers = int(os.environ.get("REPLAY_LOAD_WORKERS", "8"))
    assert 1 <= count <= 1000 and 1 <= workers <= 64

    def lifecycle(index: int) -> tuple[str, float]:
        started = perf_counter()
        created = client.post(
            BASE, json={"start_time": START.isoformat(), "end_time": END.isoformat()}
        )
        assert created.status_code == 201, created.text
        session_id = created.json()["session_id"]
        ids.append(session_id)
        path = f"{BASE}/{session_id}"
        speed = [0.25, 1.0, 4.0, 16.0][index % 4]
        target = START + timedelta(microseconds=index + 1)
        for action in [
            {"action": "speed", "speed": speed},
            {"action": "seek", "position": target.isoformat()},
            {"action": "play"},
        ]:
            response = client.patch(path, json=action)
            assert response.status_code == 200, response.text
        with Session(engine) as db:
            result = ReplaySessionService(db).advance_session(
                session_id, elapsed=timedelta(seconds=1), now=datetime(2026, 10, 3, tzinfo=UTC)
            )
            assert result is not None
        assert client.patch(path, json={"action": "pause"}).status_code == 200
        fetched = client.get(path)
        assert fetched.status_code == 200, fetched.text
        assert fetched.json()["state"] == "paused"
        assert fetched.json()["speed"] == speed
        assert datetime.fromisoformat(fetched.json()["position"]) == target + timedelta(
            seconds=speed
        )
        return session_id, perf_counter() - started

    started = perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(lifecycle, range(count)))
    duration = perf_counter() - started
    session_ids = [result[0] for result in results]
    assert len(set(session_ids)) == count
    with Session(engine) as db:
        persisted = db.scalars(
            select(ReplaySessionRecord).where(ReplaySessionRecord.session_id.in_(session_ids))
        ).all()
        assert len(persisted) == count
        assert all(record.state == "paused" for record in persisted)
    latencies = sorted(result[1] for result in results)
    p95 = latencies[max(0, (95 * count + 99) // 100 - 1)]
    print(
        f"replay_load sessions={count} workers={workers} duration_s={duration:.3f} "
        f"sessions_per_s={count / duration:.3f} lifecycle_p95_s={p95:.3f} "
        f"lifecycle_max_s={max(latencies):.3f}"
    )
