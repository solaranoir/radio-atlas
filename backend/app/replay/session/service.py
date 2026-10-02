from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy.orm import Session

from app.replay.session.models import ReplaySession
from app.replay.session.persistence import (
    get_replay_session,
    save_replay_session,
)


class ReplaySessionService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_session(
        self,
        *,
        start_time: datetime,
        end_time: datetime,
        now: datetime,
    ) -> ReplaySession:
        replay_session = ReplaySession.create(
            session_id=str(uuid4()),
            start_time=start_time,
            end_time=end_time,
            now=now,
        )

        save_replay_session(
            self._session,
            replay_session,
        )
        self._session.commit()

        return replay_session

    def get_session(
        self,
        session_id: str,
    ) -> ReplaySession | None:
        return get_replay_session(
            self._session,
            session_id,
        )

    def play_session(
        self,
        session_id: str,
        *,
        now: datetime,
    ) -> ReplaySession | None:
        replay_session = get_replay_session(
            self._session,
            session_id,
        )

        if replay_session is None:
            return None

        replay_session.play(now=now)

        save_replay_session(
            self._session,
            replay_session,
        )
        self._session.commit()

        return replay_session

    def pause_session(
        self,
        session_id: str,
        *,
        now: datetime,
    ) -> ReplaySession | None:
        replay_session = get_replay_session(
            self._session,
            session_id,
        )

        if replay_session is None:
            return None

        replay_session.pause(now=now)

        save_replay_session(
            self._session,
            replay_session,
        )
        self._session.commit()

        return replay_session

    def seek_session(
        self,
        session_id: str,
        *,
        position: datetime,
        now: datetime,
    ) -> ReplaySession | None:
        replay_session = get_replay_session(
            self._session,
            session_id,
        )

        if replay_session is None:
            return None

        replay_session.seek(
            position,
            now=now,
        )

        save_replay_session(
            self._session,
            replay_session,
        )
        self._session.commit()

        return replay_session

    def set_session_speed(
       self,
        session_id: str,
        *,
        speed: float,
        now: datetime,
    ) -> ReplaySession | None:
        replay_session = get_replay_session(
            self._session,
            session_id,
        )

        if replay_session is None:
            return None

        replay_session.set_speed(
            speed,
            now=now,
        )

        save_replay_session(
            self._session,
            replay_session,
        )
        self._session.commit()

        return replay_session

    def advance_session(
        self,
        session_id: str,
        *,
        elapsed: timedelta,
        now: datetime,
    ) -> ReplaySession | None:
        replay_session = get_replay_session(
            self._session,
            session_id,
        )

        if replay_session is None:
            return None

        replay_session.advance(
            elapsed,
            now=now,
        )

        save_replay_session(
            self._session,
            replay_session,
        )
        self._session.commit()

        return replay_session
