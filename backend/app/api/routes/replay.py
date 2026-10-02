from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, WebSocket, status
from pydantic import BaseModel

from app.api.dependencies import get_replay_session_service, get_replay_stream_coordinator
from app.replay.streaming.coordinator import ReplayStreamCoordinator
from app.replay.session.models import ReplaySession
from app.replay.session.service import ReplaySessionService

router = APIRouter(
    prefix="/replay",
    tags=["replay"],
)

class CreateReplaySessionRequest(BaseModel):
    start_time: datetime
    end_time: datetime

class ReplaySessionResponse(BaseModel):
    session_id: str
    start_time: datetime
    end_time: datetime
    position: datetime
    state: str
    speed: float
    created_at: datetime
    updated_at: datetime

class UpdateReplaySessionRequest(BaseModel):
    action: str
    position: datetime | None = None
    speed: float | None = None

class ReplayObservationResponse(BaseModel):
    id: int
    provider_id: int
    sequence_number: int | None
    sender_station_id: int | None
    receiver_station_id: int | None
    sender_callsign: str
    receiver_callsign: str
    sender_grid: str | None
    receiver_grid: str | None
    frequency_hz: int | None
    band: str | None
    mode: str
    snr_db: int | None
    observed_at: datetime
    transmitted_at: datetime | None
    sender_entity_id: int | None
    receiver_entity_id: int | None

@router.post(
    "/sessions",
    response_model=ReplaySessionResponse,
    status_code=status.HTTP_201_CREATED,
)

def create_replay_session(
    request: CreateReplaySessionRequest,
    service: Annotated[
        ReplaySessionService,
        Depends(get_replay_session_service),
    ],
) -> ReplaySession:
    return service.create_session(
        start_time=request.start_time,
        end_time=request.end_time,
        now=datetime.now(UTC),
    )

@router.get(
    "/sessions/{session_id}",
    response_model=ReplaySessionResponse,
)
def get_replay_session(
    session_id: str,
    service: Annotated[
        ReplaySessionService,
        Depends(get_replay_session_service),
    ],
) -> ReplaySession:
    replay_session = service.get_session(session_id)

    if replay_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Replay session not found",
        )

    return replay_session

@router.patch(
    "/sessions/{session_id}",
    response_model=ReplaySessionResponse,
)
def update_replay_session(
    session_id: str,
    request: UpdateReplaySessionRequest,
    service: Annotated[
        ReplaySessionService,
        Depends(get_replay_session_service),
    ],
) -> ReplaySession:
    if request.action == "play":
        replay_session = service.play_session(
            session_id,
            now=datetime.now(UTC),
        )
    elif request.action == "pause":
        replay_session = service.pause_session(
            session_id,
            now=datetime.now(UTC),
         )
    elif request.action == "seek":
        if request.position is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Position is required for seek",
            )

        replay_session = service.seek_session(
            session_id,
            position=request.position,
            now=datetime.now(UTC),
        )
    elif request.action == "speed":
        if request.speed is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Speed is required for speed change",
            )

        replay_session = service.set_session_speed(
            session_id,
            speed=request.speed,
            now=datetime.now(UTC),
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported replay action",
        )

    if replay_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Replay session not found",
        )

    return replay_session

@router.websocket("/sessions/{session_id}/stream")
async def stream_replay_session(
    websocket: WebSocket,
    session_id: str,
    service: Annotated[
        ReplaySessionService,
        Depends(get_replay_session_service),
    ],
    coordinator: Annotated[
        ReplayStreamCoordinator,
        Depends(get_replay_stream_coordinator),
    ],
) -> None:
    replay_session = service.get_session(session_id)

    await websocket.accept()

    if replay_session is None:
        await websocket.close(code=1008)
        return

    await websocket.send_json(
        {
            "type": "session",
            "session_id": replay_session.session_id,
            "state": replay_session.state.value,
            "position": replay_session.position.isoformat(),
        }
    )
