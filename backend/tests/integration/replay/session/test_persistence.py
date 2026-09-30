from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.replay.session.models import ReplaySession, ReplayState
from app.replay.session.persistence import (
    delete_replay_sessions_updated_before,
    get_replay_session,
    save_replay_session,
)


def test_save_and_load_replay_session(db_session: Session) -> None:
    now = datetime(2026, 9, 29, 12, 0, tzinfo=UTC)
    start_time = datetime(2026, 9, 1, 10, 0, tzinfo=UTC)
    end_time = datetime(2026, 9, 1, 11, 0, tzinfo=UTC)

    replay_session = ReplaySession.create(
        session_id="test-session",
        start_time=start_time,
        end_time=end_time,
        now=now,
    )
    replay_session.play(now=now)
    replay_session.set_speed(2.0, now=now)

    save_replay_session(db_session, replay_session)
    db_session.flush()
    db_session.expire_all()

    loaded = get_replay_session(db_session, "test-session")

    assert loaded is not None
    assert loaded.session_id == replay_session.session_id
    assert loaded.start_time == replay_session.start_time
    assert loaded.end_time == replay_session.end_time
    assert loaded.position == replay_session.position
    assert loaded.state is ReplayState.PLAYING
    assert loaded.speed == 2.0
    assert loaded.created_at == replay_session.created_at
    assert loaded.updated_at == replay_session.updated_at


def test_save_updates_existing_replay_session(db_session: Session) -> None:
    created_at = datetime(2026, 9, 29, 12, 0, tzinfo=UTC)
    updated_at = datetime(2026, 9, 29, 12, 5, tzinfo=UTC)
    start_time = datetime(2026, 9, 1, 10, 0, tzinfo=UTC)
    end_time = datetime(2026, 9, 1, 11, 0, tzinfo=UTC)
    new_position = datetime(2026, 9, 1, 10, 30, tzinfo=UTC)

    replay_session = ReplaySession.create(
        session_id="test-session-update",
        start_time=start_time,
        end_time=end_time,
        now=created_at,
    )

    save_replay_session(db_session, replay_session)
    db_session.flush()

    replay_session.play(now=updated_at)
    replay_session.seek(new_position, now=updated_at)
    replay_session.set_speed(4.0, now=updated_at)

    save_replay_session(db_session, replay_session)
    db_session.flush()
    db_session.expire_all()

    loaded = get_replay_session(db_session, replay_session.session_id)

    assert loaded is not None
    assert loaded.position == new_position
    assert loaded.state is ReplayState.PLAYING
    assert loaded.speed == 4.0
    assert loaded.created_at == created_at
    assert loaded.updated_at == updated_at


def test_delete_replay_sessions_updated_before(db_session: Session) -> None:
    stale_time = datetime(2026, 9, 29, 10, 0, tzinfo=UTC)
    cutoff = datetime(2026, 9, 29, 11, 0, tzinfo=UTC)
    fresh_time = datetime(2026, 9, 29, 12, 0, tzinfo=UTC)
    start_time = datetime(2026, 9, 1, 10, 0, tzinfo=UTC)
    end_time = datetime(2026, 9, 1, 11, 0, tzinfo=UTC)

    stale_session = ReplaySession.create(
        session_id="stale-session",
        start_time=start_time,
        end_time=end_time,
        now=stale_time,
    )
    fresh_session = ReplaySession.create(
        session_id="fresh-session",
        start_time=start_time,
        end_time=end_time,
        now=fresh_time,
    )

    save_replay_session(db_session, stale_session)
    save_replay_session(db_session, fresh_session)
    db_session.flush()

    deleted_count = delete_replay_sessions_updated_before(
        db_session,
        cutoff,
    )
    db_session.flush()

    assert deleted_count == 1
    assert get_replay_session(db_session, "stale-session") is None
    assert get_replay_session(db_session, "fresh-session") is not None
