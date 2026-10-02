from datetime import UTC, datetime, timedelta
from unittest.mock import Mock, MagicMock, patch

from sqlalchemy.orm import Session

from app.replay.session.models import ReplaySession
from app.replay.session.service import ReplaySessionService

NOW = datetime(2026, 9, 30, 12, 0, tzinfo=UTC)


def test_service_accepts_database_session() -> None:
    db = Mock(spec=Session)

    service = ReplaySessionService(db)

    assert service._session is db

def test_create_session_initializes_replay_session() -> None:
    db = Mock(spec=Session)
    service = ReplaySessionService(db)

    start_time = datetime(2026, 9, 1, 10, 0, tzinfo=UTC)
    end_time = datetime(2026, 9, 1, 11, 0, tzinfo=UTC)

    replay_session = service.create_session(
        start_time=start_time,
        end_time=end_time,
        now=NOW,
    )

    assert replay_session.start_time == start_time
    assert replay_session.end_time == end_time
    assert replay_session.position == start_time
    assert replay_session.speed == 1.0
    assert replay_session.created_at == NOW
    assert replay_session.updated_at == NOW
    assert replay_session.session_id

def test_create_session_persists_session() -> None:
    db = Mock(spec=Session)
    service = ReplaySessionService(db)

    with patch(
        "app.replay.session.service.save_replay_session"
    ) as save_replay_session:
        replay_session = service.create_session(
            start_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
            end_time=datetime(2026, 9, 1, 11, 0, tzinfo=UTC),
            now=NOW,
        )

    save_replay_session.assert_called_once_with(
        db,
        replay_session,
    )

def test_create_session_commits_transaction() -> None:
    db = Mock(spec=Session)
    service = ReplaySessionService(db)

    with patch(
        "app.replay.session.service.save_replay_session"
    ):
        service.create_session(
            start_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
            end_time=datetime(2026, 9, 1, 11, 0, tzinfo=UTC),
            now=NOW,
        )

    db.commit.assert_called_once_with()

def test_get_session_returns_persisted_session() -> None:
    db = Mock(spec=Session)
    service = ReplaySessionService(db)

    expected = ReplaySession.create(
        session_id="test-session",
        start_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 11, 0, tzinfo=UTC),
        now=NOW,
    )

    with patch(
        "app.replay.session.service.get_replay_session",
        return_value=expected,
    ) as get_replay_session:
        result = service.get_session("test-session")

    assert result is expected
    get_replay_session.assert_called_once_with(
        db,
        "test-session",
    )

def test_play_session_updates_and_persists_session() -> None:
    db = Mock(spec=Session)
    service = ReplaySessionService(db)

    replay_session = ReplaySession.create(
        session_id="test-session",
        start_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 11, 0, tzinfo=UTC),
        now=NOW,
    )
    updated_at = datetime(2026, 9, 30, 12, 1, tzinfo=UTC)

    with (
        patch(
            "app.replay.session.service.get_replay_session",
            return_value=replay_session,
        ),
        patch(
            "app.replay.session.service.save_replay_session"
        ) as save_replay_session,
    ):
        result = service.play_session(
            "test-session",
            now=updated_at,
        )

    assert result is replay_session
    assert replay_session.state.value == "playing"
    assert replay_session.updated_at == updated_at
    save_replay_session.assert_called_once_with(
        db,
        replay_session,
    )
    db.commit.assert_called_once_with()

def test_pause_session_updates_and_persists_session() -> None:
    db = Mock(spec=Session)
    service = ReplaySessionService(db)

    replay_session = ReplaySession.create(
        session_id="test-session",
        start_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 11, 0, tzinfo=UTC),
        now=NOW,
    )
    replay_session.play(now=NOW)

    updated_at = datetime(2026, 9, 30, 12, 1, tzinfo=UTC)

    with (
        patch(
            "app.replay.session.service.get_replay_session",
            return_value=replay_session,
        ),
        patch(
            "app.replay.session.service.save_replay_session"
        ) as save_replay_session,
    ):
        result = service.pause_session(
            "test-session",
            now=updated_at,
        )

    assert result is replay_session
    assert replay_session.state.value == "paused"
    assert replay_session.updated_at == updated_at
    save_replay_session.assert_called_once_with(
        db,
        replay_session,
    )
    db.commit.assert_called_once_with()

def test_seek_session_updates_and_persists_position() -> None:
    db = Mock(spec=Session)
    service = ReplaySessionService(db)

    replay_session = ReplaySession.create(
        session_id="test-session",
        start_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 11, 0, tzinfo=UTC),
        now=NOW,
    )
    position = datetime(2026, 9, 1, 10, 30, tzinfo=UTC)
    updated_at = datetime(2026, 9, 30, 12, 1, tzinfo=UTC)

    with (
        patch(
            "app.replay.session.service.get_replay_session",
            return_value=replay_session,
        ),
        patch(
            "app.replay.session.service.save_replay_session"
        ) as save_replay_session,
    ):
        result = service.seek_session(
            "test-session",
            position=position,
            now=updated_at,
        )

    assert result is replay_session
    assert replay_session.position == position
    assert replay_session.updated_at == updated_at
    save_replay_session.assert_called_once_with(
        db,
        replay_session,
    )
    db.commit.assert_called_once_with()

def test_set_session_speed_updates_and_persists_speed() -> None:
    db = Mock(spec=Session)
    service = ReplaySessionService(db)

    replay_session = ReplaySession.create(
        session_id="test-session",
        start_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 11, 0, tzinfo=UTC),
        now=NOW,
    )
    updated_at = datetime(2026, 9, 30, 12, 1, tzinfo=UTC)

    with (
        patch(
            "app.replay.session.service.get_replay_session",
            return_value=replay_session,
        ),
        patch(
            "app.replay.session.service.save_replay_session"
        ) as save_replay_session,
    ):
        result = service.set_session_speed(
            "test-session",
            speed=2.0,
            now=updated_at,
        )

    assert result is replay_session
    assert replay_session.speed == 2.0
    assert replay_session.updated_at == updated_at
    save_replay_session.assert_called_once_with(
        db,
        replay_session,
    )
    db.commit.assert_called_once_with()

def test_advance_session_persists_updated_position() -> None:
    replay_session = ReplaySession.create(
        session_id="test-session",
        start_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 9, 1, 11, 0, tzinfo=UTC),
        now=datetime(2026, 9, 30, 12, 0, tzinfo=UTC),
    )
    replay_session.play(
        now=datetime(2026, 9, 30, 12, 1, tzinfo=UTC),
    )

    db_session = MagicMock()
    service = ReplaySessionService(db_session)

    with (
        patch(
            "app.replay.session.service.get_replay_session",
            return_value=replay_session,
        ),
        patch(
            "app.replay.session.service.save_replay_session",
        ) as save_replay_session,
    ):
        result = service.advance_session(
            "test-session",
            elapsed=timedelta(seconds=10),
            now=datetime(2026, 9, 30, 12, 1, 10, tzinfo=UTC),
        )

    assert result is replay_session
    assert replay_session.position == datetime(
        2026,
        9,
        1,
        10,
        0,
        10,
        tzinfo=UTC,
    )
    save_replay_session.assert_called_once_with(
        db_session,
        replay_session,
    )
    db_session.commit.assert_called_once_with()
