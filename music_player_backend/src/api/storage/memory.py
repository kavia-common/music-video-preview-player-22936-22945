import os
from typing import Dict, Any

# Simple in-memory stores for demo purposes
db_users: Dict[str, Dict[str, Any]] = {}
db_tracks: Dict[str, Dict[str, Any]] = {}
TokenIndex: Dict[str, str] = {}
playback_state: Dict[str, Dict[str, Any]] = {}

def media_root() -> str:
    """Base folder for storing uploaded media files."""
    root = os.getenv("MUSIC_MEDIA_ROOT", "/tmp/music_media")
    os.makedirs(root, exist_ok=True)
    return root

def media_root_path(*parts: str) -> str:
    """Join parts to the media root path."""
    return os.path.join(media_root(), *parts)
