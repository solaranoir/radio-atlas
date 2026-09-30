from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.replay.session.persistence import delete_replay_sessions_updated_before


def cleanup_expired_replay_sessions(
    db: Session,
    *,
    now: datetime,
    ttl_seconds: int,
) -> int:
    if ttl_seconds <= 0:
        raise ValueError("replay session TTL must be greater than zero")

    cutoff = now - timedelta(seconds=ttl_seconds)

    return delete_replay_sessions_updated_before(
        db,
        cutoff,
    )
