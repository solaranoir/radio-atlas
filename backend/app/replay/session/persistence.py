from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.infrastructure.database.models import ReplaySessionRecord
from app.replay.session.models import ReplaySession, ReplayState


def save_replay_session(
    db: Session,
    replay_session: ReplaySession,
) -> None:
    statement = insert(ReplaySessionRecord).values(
        session_id=replay_session.session_id,
        start_time=replay_session.start_time,
        end_time=replay_session.end_time,
        position=replay_session.position,
        state=replay_session.state.value,
        speed=replay_session.speed,
        created_at=replay_session.created_at,
        updated_at=replay_session.updated_at,
    )

    statement = statement.on_conflict_do_update(
        index_elements=[ReplaySessionRecord.session_id],
        set_={
            "start_time": statement.excluded.start_time,
            "end_time": statement.excluded.end_time,
            "position": statement.excluded.position,
            "state": statement.excluded.state,
            "speed": statement.excluded.speed,
            "created_at": statement.excluded.created_at,
            "updated_at": statement.excluded.updated_at,
        },
    )

    db.execute(statement)


def get_replay_session(
    db: Session,
    session_id: str,
) -> ReplaySession | None:
    statement = select(ReplaySessionRecord).where(ReplaySessionRecord.session_id == session_id)
    record = db.scalar(statement)

    if record is None:
        return None

    return ReplaySession(
        session_id=record.session_id,
        start_time=record.start_time,
        end_time=record.end_time,
        position=record.position,
        state=ReplayState(record.state),
        speed=record.speed,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def delete_replay_sessions_updated_before(
    db: Session,
    cutoff: datetime,
) -> int:
    statement = (
        delete(ReplaySessionRecord)
        .where(ReplaySessionRecord.updated_at < cutoff)
        .returning(ReplaySessionRecord.session_id)
    )

    deleted_session_ids = db.scalars(statement).all()

    return len(deleted_session_ids)
