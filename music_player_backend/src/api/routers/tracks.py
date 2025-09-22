from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Response, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
import secrets
import os
from ..storage.memory import db_tracks, media_root_path
from .users import get_current_user, UserPublic

router = APIRouter()


class TrackCreateResponse(BaseModel):
    id: str = Field(..., description="Track ID")
    title: str = Field(..., description="Track title")
    artist: str = Field(..., description="Artist name")
    duration_sec: Optional[int] = Field(None, description="Duration in seconds")
    has_glimpse: bool = Field(False, description="Whether a video glimpse is attached")


class TrackUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, description="Track title")
    artist: Optional[str] = Field(None, description="Artist name")
    duration_sec: Optional[int] = Field(None, description="Duration in seconds")


class TrackListItem(TrackCreateResponse):
    pass


def _ensure_media_dir():
    os.makedirs(media_root_path("audio"), exist_ok=True)


@router.post(
    "",
    summary="Create Track (Upload)",
    description="Upload an audio file and create a track metadata entry.",
    response_model=TrackCreateResponse,
    status_code=201,
)
# PUBLIC_INTERFACE
async def create_track(
    title: str = Form(...),
    artist: str = Form(...),
    duration_sec: Optional[int] = Form(None),
    audio: UploadFile = File(...),
    user: UserPublic = Depends(get_current_user),
):
    """Create a new track with uploaded audio file."""
    if not audio.content_type or not audio.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid audio file")
    _ensure_media_dir()
    track_id = secrets.token_hex(8)
    filename = f"{track_id}_{audio.filename}"
    dest = media_root_path("audio", filename)
    # Save file
    with open(dest, "wb") as f:
        f.write(await audio.read())
    db_tracks[track_id] = {
        "id": track_id,
        "title": title,
        "artist": artist,
        "duration_sec": int(duration_sec) if duration_sec is not None else None,
        "audio_path": dest,
        "owner_id": user.id,
        "glimpse_path": None,
    }
    return TrackCreateResponse(
        id=track_id,
        title=title,
        artist=artist,
        duration_sec=db_tracks[track_id]["duration_sec"],
        has_glimpse=False,
    )


@router.get(
    "",
    summary="List Tracks",
    description="List all tracks in the library.",
    response_model=List[TrackListItem],
)
# PUBLIC_INTERFACE
def list_tracks():
    """Return list of tracks."""
    items = []
    for t in db_tracks.values():
        items.append(
            TrackListItem(
                id=t["id"],
                title=t["title"],
                artist=t["artist"],
                duration_sec=t["duration_sec"],
                has_glimpse=bool(t["glimpse_path"]),
            )
        )
    return items


@router.get(
    "/{track_id}",
    summary="Get Track",
    description="Fetch a track's metadata by ID.",
    response_model=TrackCreateResponse,
)
# PUBLIC_INTERFACE
def get_track(track_id: str):
    """Retrieve track metadata."""
    t = db_tracks.get(track_id)
    if not t:
        raise HTTPException(status_code=404, detail="Track not found")
    return TrackCreateResponse(
        id=t["id"],
        title=t["title"],
        artist=t["artist"],
        duration_sec=t["duration_sec"],
        has_glimpse=bool(t["glimpse_path"]),
    )


@router.patch(
    "/{track_id}",
    summary="Update Track",
    description="Update track metadata fields.",
    response_model=TrackCreateResponse,
)
# PUBLIC_INTERFACE
def update_track(track_id: str, body: TrackUpdateRequest, user: UserPublic = Depends(get_current_user)):
    """Update track fields (title, artist, duration)."""
    t = db_tracks.get(track_id)
    if not t:
        raise HTTPException(status_code=404, detail="Track not found")
    if t["owner_id"] != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    if body.title is not None:
        t["title"] = body.title
    if body.artist is not None:
        t["artist"] = body.artist
    if body.duration_sec is not None:
        t["duration_sec"] = int(body.duration_sec)
    return TrackCreateResponse(
        id=t["id"],
        title=t["title"],
        artist=t["artist"],
        duration_sec=t["duration_sec"],
        has_glimpse=bool(t["glimpse_path"]),
    )


@router.delete(
    "/{track_id}",
    summary="Delete Track",
    description="Delete a track and its audio file.",
    status_code=204,
)
# PUBLIC_INTERFACE
def delete_track(track_id: str, user: UserPublic = Depends(get_current_user)):
    """Delete a track and remove its audio from disk."""
    t = db_tracks.get(track_id)
    if not t:
        raise HTTPException(status_code=404, detail="Track not found")
    if t["owner_id"] != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    # remove files
    if t.get("audio_path") and os.path.exists(t["audio_path"]):
        try:
            os.remove(t["audio_path"])
        except OSError:
            pass
    if t.get("glimpse_path") and os.path.exists(t["glimpse_path"]):
        try:
            os.remove(t["glimpse_path"])
        except OSError:
            pass
    del db_tracks[track_id]
    return Response(status_code=204)


@router.get(
    "/{track_id}/stream",
    summary="Stream Audio",
    description="Stream audio bytes for a given track.",
    responses={200: {"content": {"audio/mpeg": {}}, "description": "Audio stream returned"}},
)
# PUBLIC_INTERFACE
def stream_track(track_id: str):
    """Return audio file bytes for streaming."""
    t = db_tracks.get(track_id)
    if not t:
        raise HTTPException(status_code=404, detail="Track not found")
    path = t.get("audio_path")
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    # naive: read all bytes; for production use ranges/StreamingResponse
    with open(path, "rb") as f:
        data = f.read()
    return Response(content=data, media_type="audio/mpeg")
