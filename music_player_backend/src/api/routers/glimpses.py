from fastapi import APIRouter, UploadFile, File, HTTPException, Response, Depends
from pydantic import BaseModel, Field
import os
from ..storage.memory import db_tracks, media_root_path
from .users import get_current_user, UserPublic

router = APIRouter()


class GlimpseInfo(BaseModel):
    track_id: str = Field(..., description="Associated track ID")
    has_glimpse: bool = Field(..., description="Whether a glimpse is attached")


def _ensure_video(file: UploadFile):
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Invalid video file")


def _ensure_track(track_id: str):
    if track_id not in db_tracks:
        raise HTTPException(status_code=404, detail="Track not found")


@router.post(
    "/{track_id}",
    summary="Attach Video Glimpse",
    description="Upload and attach a short video glimpse to a track.",
    response_model=GlimpseInfo,
    status_code=201,
)
# PUBLIC_INTERFACE
async def attach_glimpse(track_id: str, video: UploadFile = File(...), user: UserPublic = Depends(get_current_user)):
    """Attach a video glimpse to an existing track."""
    _ensure_track(track_id)
    _ensure_video(video)
    t = db_tracks[track_id]
    if t["owner_id"] != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    os.makedirs(media_root_path("glimpses"), exist_ok=True)
    filename = f"{track_id}_{video.filename}"
    dest = media_root_path("glimpses", filename)
    with open(dest, "wb") as f:
        f.write(await video.read())
    t["glimpse_path"] = dest
    return GlimpseInfo(track_id=track_id, has_glimpse=True)


@router.get(
    "/{track_id}",
    summary="Has Glimpse",
    description="Check whether a track has an attached video glimpse.",
    response_model=GlimpseInfo,
)
# PUBLIC_INTERFACE
def has_glimpse(track_id: str):
    """Return whether the track has a glimpse attached."""
    _ensure_track(track_id)
    t = db_tracks[track_id]
    return GlimpseInfo(track_id=track_id, has_glimpse=bool(t.get("glimpse_path")))


@router.get(
    "/{track_id}/stream",
    summary="Stream Video Glimpse",
    description="Stream the video glimpse for a track if present.",
    responses={200: {"content": {"video/mp4": {}}, "description": "Video stream returned"}},
)
# PUBLIC_INTERFACE
def stream_glimpse(track_id: str):
    """Stream the video glimpse bytes for the given track."""
    _ensure_track(track_id)
    t = db_tracks[track_id]
    path = t.get("glimpse_path")
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Glimpse not found")
    with open(path, "rb") as f:
        data = f.read()
    # Defaulting to MP4; in a real system infer media type by file extension or content
    return Response(content=data, media_type="video/mp4")


@router.delete(
    "/{track_id}",
    summary="Delete Video Glimpse",
    description="Remove the video glimpse from a track.",
    status_code=204,
)
# PUBLIC_INTERFACE
def delete_glimpse(track_id: str, user: UserPublic = Depends(get_current_user)):
    """Delete the attached glimpse for the track."""
    _ensure_track(track_id)
    t = db_tracks[track_id]
    if t["owner_id"] != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    path = t.get("glimpse_path")
    if path and os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass
    t["glimpse_path"] = None
    return Response(status_code=204)
