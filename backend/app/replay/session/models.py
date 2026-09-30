from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum


class ReplayState(StrEnum):
    PAUSED = "paused"
    PLAYING = "playing"
    COMPLETED = "completed"


@dataclass
class ReplaySession:
    session_id: str
    start_time: datetime
    end_time: datetime
    position: datetime
    state: ReplayState
    speed: float
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        *,
        session_id: str,
        start_time: datetime,
        end_time: datetime,
        now: datetime,
    ) -> "ReplaySession":
        if start_time >= end_time:
            raise ValueError("start_time must be before end_time")

        return cls(
            session_id=session_id,
            start_time=start_time,
            end_time=end_time,
            position=start_time,
            state=ReplayState.PAUSED,
            speed=1.0,
            created_at=now,
            updated_at=now,
        )

    def play(self, *, now: datetime) -> None:
        if self.state in {ReplayState.PLAYING, ReplayState.COMPLETED}:
            return

        self.state = ReplayState.PLAYING
        self.updated_at = now

    def pause(self, *, now: datetime) -> None:
        if self.state is not ReplayState.PLAYING:
            return

        self.state = ReplayState.PAUSED
        self.updated_at = now

    def seek(self, position: datetime, *, now: datetime) -> None:
        if position < self.start_time or position > self.end_time:
            raise ValueError("position must be within replay window")

        self.position = position

        if position == self.end_time:
            self.state = ReplayState.COMPLETED
        elif self.state is ReplayState.COMPLETED:
            self.state = ReplayState.PAUSED

        self.updated_at = now

    def set_speed(self, speed: float, now: datetime) -> None:
        if not speed > 0:
            raise ValueError("playback speed must be greater than zero")
        self.speed = speed
        self.updated_at = now

    def advance(self, elapsed: timedelta, *, now: datetime) -> None:
        if elapsed < timedelta(0):
            raise ValueError("elapsed time must not be negative")
        if self.state is not ReplayState.PLAYING:
            return

        historical_elapsed = elapsed * self.speed
        new_position = self.position + historical_elapsed

        if new_position >= self.end_time:
            self.position = self.end_time
            self.state = ReplayState.COMPLETED
            self.updated_at = now
            return

        self.position = new_position
        self.updated_at = now
