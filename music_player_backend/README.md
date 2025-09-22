# Music Player Backend (FastAPI)

Ocean Professional themed REST API for a music player with video glimpse previews.

Endpoints
- Users: /api/users/signup, /api/users/login, /api/users/me
- Tracks: /api/tracks (POST upload), /api/tracks (GET list), /api/tracks/{id} (GET/PATCH/DELETE), /api/tracks/{id}/stream (GET)
- Playback: /api/playback/state (GET), /api/playback/play (POST), /api/playback/pause (POST), /api/playback/skip (POST)
- Glimpses: /api/glimpses/{track_id} (POST upload, GET check, DELETE), /api/glimpses/{track_id}/stream (GET)

Run locally
1. Create a virtualenv and install requirements.txt
2. export MUSIC_MEDIA_ROOT=/tmp/music_media (optional)
3. export MUSIC_BACKEND_SECRET=super-secret (set in production)
4. uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload

Auth
- Use /api/users/signup or /api/users/login to obtain a bearer token.
- Include Authorization: Bearer <token> for protected endpoints.

Note: This demo uses in-memory storage. Files are stored under MUSIC_MEDIA_ROOT.
