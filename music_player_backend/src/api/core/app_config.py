from typing import Dict, Any
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

THEME = {
    "name": "Ocean Professional",
    "primary": "#2563EB",
    "secondary": "#F59E0B",
    "background": "#f9fafb",
    "surface": "#ffffff",
    "text": "#111827",
}

def get_app_metadata() -> Dict[str, Any]:
    """Return app-level metadata configured to reflect Ocean Professional theme."""
    return {
        "title": "Music Player Backend",
        "description": (
            "Modern REST API for a music player with video glimpses.\n\n"
            f"Theme: {THEME['name']} — blue & amber accents.\n"
            "Features:\n"
            "- User signup/login/profile\n"
            "- Track upload, CRUD, and audio streaming\n"
            "- Playback state controls (play/pause/skip)\n"
            "- Video glimpse upload/stream/delete per track"
        ),
        "version": "1.0.0",
        "contact": {"name": "API Support", "email": "support@example.com"},
        "license_info": {"name": "MIT"},
        "terms_of_service": "https://example.com/terms",
        "openapi_tags": [
            {"name": "System", "description": "System and docs endpoints"},
            {"name": "Users", "description": "User authentication and profile"},
            {"name": "Tracks", "description": "Music track management and streaming"},
            {"name": "Playback", "description": "Playback state controls"},
            {"name": "Video Glimpses", "description": "Attach and stream video previews"},
        ],
    }


def openapi_overrides(app: FastAPI) -> None:
    """Customize Swagger UI assets colors via OpenAPI custom properties if desired."""
    # Additional extensions can be used by a custom docs UI if integrated later.
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        openapi_schema["info"]["x-theme"] = THEME
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi
