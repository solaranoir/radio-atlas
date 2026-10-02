import pytest

from datetime import UTC, datetime
from unittest.mock import Mock

from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.api.dependencies import (
    get_replay_session_service,
    get_replay_stream_coordinator,
)
from app.main import create_app
from app.replay.session.models import ReplaySession
from app.replay.session.service import ReplaySessionService
from app.replay.streaming.coordinator import ReplayStreamCoordinator

def _client(
    service: ReplaySessionService,
    coordinator: ReplayStreamCoordinator | None = None,
) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_replay_session_service] = lambda: service

    if coordinator is not None:
        app.dependency_overrides[get_replay_stream_coordinator] = lambda: coordinator

    return TestClient(app)

def test_create_replay_session_returns_201() -> None:
    service = Mock(spec=ReplaySessionService)
    service.create_session.return_value = ReplaySession.create(
        session_id="test-session",
        start_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 11, 0, tzinfo=UTC),
        now=datetime(2026, 9, 30, 12, 0, tzinfo=UTC),
    )

    client = _client(service)

    response = client.post(
        "/api/v1/replay/sessions",
        json={
            "start_time": "2026-09-01T10:00:00Z",
            "end_time": "2026-09-01T11:00:00Z",
        },
    )

    assert response.status_code == 201
    service.create_session.assert_called_once()

    call = service.create_session.call_args

    assert call.kwargs["start_time"] == datetime(
        2026,
        9,
        1,
        10,
        0,
        tzinfo=UTC,
    )
    assert call.kwargs["end_time"] == datetime(
        2026,
        9,
        1,
        11,
        0,
        tzinfo=UTC,
    )
    assert call.kwargs["now"].tzinfo is UTC
    assert response.json() == {
        "session_id": "test-session",
        "start_time": "2026-09-01T10:00:00Z",
        "end_time": "2026-09-01T11:00:00Z",
        "position": "2026-09-01T10:00:00Z",
        "state": "paused",
        "speed": 1.0,
        "created_at": "2026-09-30T12:00:00Z",
        "updated_at": "2026-09-30T12:00:00Z",
    }

def test_get_replay_session_returns_session() -> None:
    service = Mock(spec=ReplaySessionService)
    service.get_session.return_value = ReplaySession.create(
        session_id="test-session",
        start_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 11, 0, tzinfo=UTC),
        now=datetime(2026, 9, 30, 12, 0, tzinfo=UTC),
    )

    client = _client(service)

    response = client.get(
        "/api/v1/replay/sessions/test-session",
    )

    assert response.status_code == 200
    assert response.json()["session_id"] == "test-session"
    service.get_session.assert_called_once_with("test-session")

def test_get_replay_session_returns_404_when_missing() -> None:
    service = Mock(spec=ReplaySessionService)
    service.get_session.return_value = None

    client = _client(service)

    response = client.get(
        "/api/v1/replay/sessions/missing-session",
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Replay session not found",
    }
    service.get_session.assert_called_once_with(
        "missing-session",
    )

def test_patch_replay_session_plays_session() -> None:
    service = Mock(spec=ReplaySessionService)
            
    replay_session = ReplaySession.create(
        session_id="test-session",
        start_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 11, 0, tzinfo=UTC),
        now=datetime(2026, 9, 30, 12, 0, tzinfo=UTC),
    )
    replay_session.play(
        now=datetime(2026, 9, 30, 12, 1, tzinfo=UTC),
    )
    service.play_session.return_value = replay_session

    client = _client(service)
           
    response = client.patch(
        "/api/v1/replay/sessions/test-session",
        json={
            "action": "play",
        },
    )
    
    assert response.status_code == 200
    assert response.json()["state"] == "playing"
        
    service.play_session.assert_called_once()
    call = service.play_session.call_args
     
    assert call.args == ("test-session",)
    assert call.kwargs["now"].tzinfo is UTC
     
def test_patch_replay_session_pauses_session() -> None:
    service = Mock(spec=ReplaySessionService)

    replay_session = ReplaySession.create(
        session_id="test-session",
        start_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 11, 0, tzinfo=UTC),
        now=datetime(2026, 9, 30, 12, 0, tzinfo=UTC),
    )
    replay_session.play(
        now=datetime(2026, 9, 30, 12, 1, tzinfo=UTC),
    )
    replay_session.pause(
        now=datetime(2026, 9, 30, 12, 2, tzinfo=UTC),
    )
    service.pause_session.return_value = replay_session

    client = _client(service)

    response = client.patch(
        "/api/v1/replay/sessions/test-session",
        json={
            "action": "pause",
        },
    )

    assert response.status_code == 200
    assert response.json()["state"] == "paused"

    service.pause_session.assert_called_once()
    call = service.pause_session.call_args

    assert call.args == ("test-session",)
    assert call.kwargs["now"].tzinfo is UTC

def test_patch_replay_session_seeks_session() -> None:
    service = Mock(spec=ReplaySessionService)

    replay_session = ReplaySession.create(
        session_id="test-session",
        start_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 11, 0, tzinfo=UTC),
        now=datetime(2026, 9, 30, 12, 0, tzinfo=UTC),
    )
    position = datetime(2026, 9, 1, 10, 30, tzinfo=UTC)
    replay_session.seek(
        position,
        now=datetime(2026, 9, 30, 12, 1, tzinfo=UTC),
    )
    service.seek_session.return_value = replay_session

    client = _client(service)

    response = client.patch(
        "/api/v1/replay/sessions/test-session",
        json={
            "action": "seek",
            "position": "2026-09-01T10:30:00Z",
        },
    )

    assert response.status_code == 200
    assert response.json()["position"] == "2026-09-01T10:30:00Z"

    service.seek_session.assert_called_once()
    call = service.seek_session.call_args

    assert call.args == ("test-session",)
    assert call.kwargs["position"] == position
    assert call.kwargs["now"].tzinfo is UTC
def test_patch_replay_session_sets_speed() -> None:
    service = Mock(spec=ReplaySessionService)

    replay_session = ReplaySession.create(
        session_id="test-session",
        start_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 11, 0, tzinfo=UTC),
        now=datetime(2026, 9, 30, 12, 0, tzinfo=UTC),
    )
    replay_session.set_speed(
        2.0,
        now=datetime(2026, 9, 30, 12, 1, tzinfo=UTC),
    )
    service.set_session_speed.return_value = replay_session

    client = _client(service)

    response = client.patch(
        "/api/v1/replay/sessions/test-session",
        json={
            "action": "speed",
            "speed": 2.0,
        },
    )

    assert response.status_code == 200
    assert response.json()["speed"] == 2.0

    service.set_session_speed.assert_called_once()
    call = service.set_session_speed.call_args

    assert call.args == ("test-session",)
    assert call.kwargs["speed"] == 2.0
    assert call.kwargs["now"].tzinfo is UTC

def test_patch_replay_session_seek_requires_position() -> None:
    service = Mock(spec=ReplaySessionService)
    client = _client(service)

    response = client.patch(
        "/api/v1/replay/sessions/test-session",
        json={
            "action": "seek",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Position is required for seek",
    }
    service.seek_session.assert_not_called()

def test_patch_replay_session_speed_requires_value() -> None:
    service = Mock(spec=ReplaySessionService)
    client = _client(service)

    response = client.patch(
        "/api/v1/replay/sessions/test-session",
        json={
            "action": "speed",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Speed is required for speed change",
    }
    service.set_session_speed.assert_not_called()

def test_patch_replay_session_rejects_unsupported_action() -> None:
    service = Mock(spec=ReplaySessionService)
    client = _client(service)

    response = client.patch(
        "/api/v1/replay/sessions/test-session",
        json={
            "action": "rewind",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Unsupported replay action",
    }

    service.play_session.assert_not_called()
    service.pause_session.assert_not_called()
    service.seek_session.assert_not_called()
    service.set_session_speed.assert_not_called()

def test_replay_websocket_accepts_valid_session() -> None:
    service = Mock(spec=ReplaySessionService)

    replay_session = ReplaySession.create(
        session_id="test-session",
        start_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 11, 0, tzinfo=UTC),
        now=datetime(2026, 9, 30, 12, 0, tzinfo=UTC),
    )
    service.get_session.return_value = replay_session

    client = _client(service)

    with client.websocket_connect(
        "/api/v1/replay/sessions/test-session/stream"
    ) as websocket:
        message = websocket.receive_json()

    assert message["type"] == "session"
    assert message["session_id"] == "test-session"
    assert message["state"] == "paused"
    assert message["position"] == "2026-09-01T10:00:00+00:00"

    service.get_session.assert_called_once_with("test-session")

def test_replay_websocket_closes_for_missing_session() -> None:
    service = Mock(spec=ReplaySessionService)
    service.get_session.return_value = None

    client = _client(service)

    with (
        client.websocket_connect(
            "/api/v1/replay/sessions/missing-session/stream"
        ) as websocket,
        pytest.raises(WebSocketDisconnect) as exc_info,
    ):
        websocket.receive_json()

    assert exc_info.value.code == 1008
    service.get_session.assert_called_once_with("missing-session")

