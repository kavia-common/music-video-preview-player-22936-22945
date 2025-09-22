from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
from ..storage.memory import playback_state, db_tracks
from .users import get_current_user, UserPublic

router = APIRouter()


class PlaybackState(BaseModel):
    is_playing: bool = Field(..., description="Whether playback is active")
    current_track_id: Optional[str] = Field(None, description="Currently selected track ID")
    position_ms: int = Field(0, description="Playback position in milliseconds")


def _ensure_track(track_id: Optional[str]):
    if track_id is None:
        return
    if track_id not in db_tracks:
        raise HTTPException(status_code=404, detail="Track not found")


@router.get(
    "/state",
    summary="Get Playback State",
    description="Retrieve the user's current playback state.",
    response_model=PlaybackState,
)
# PUBLIC_INTERFACE
def get_state(user: UserPublic = Depends(get_current_user)):
    """Return current playback state for the user."""
    state = playback_state.get(user.id, {"is_playing": False, "current_track_id": None, "position_ms": 0})
    return PlaybackState(**state)


@router.post(
    "/play",
    summary="Play",
    description="Begin or resume playback of a track. If track_id is provided, switches to it.",
    response_model=PlaybackState,
)
# PUBLIC_INTERFACE
def play(track_id: Optional[str] = None, user: UserPublic = Depends(get_current_user)):
    """Start or resume playback."""
    _ensure_track(track_id)
    state = playback_state.get(user.id, {"is_playing": False, "current_track_id": None, "position_ms": 0})
    if track_id is not None:
        state["current_track_id"] = track_id
        state["position_ms"] = 0
    state["is_playing"] = True
    playback_state[user.id] = state
    return PlaybackState(**state)


@router.post(
    "/pause",
    summary="Pause",
    description="Pause the current playback.",
    response_model=PlaybackState,
)
# PUBLIC_INTERFACE
def pause(user: UserPublic = Depends(get_current_user)):
    """Pause playback."""
    state = playback_state.get(user.id, {"is_playing": False, "current_track_id": None, "position_ms": 0})
    state["is_playing"] = False
    playback_state[user.id] = state
    return PlaybackState(**state)


@router.post(
    "/skip",
    summary="Skip",
    description="Skip to a different track by ID.",
    response_model=PlaybackState,
)
# PUBLIC_INTERFACE
def skip(track_id: str, user: UserPublic = Depends(get_current_user)):
    """Skip to a specified track."""
    _ensure_track(track_id)
    state = playback_state.get(user.id, {"is_playing": False, "current_track_id": None, "position_ms": 0})
    state["current_track_id"] = track_id
    state["position_ms"] = 0
    state["is_playing"] = True
    playback_state[user.id] = state
    return PlaybackState(**state)
