from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import users, tracks, playback, glimpses
from .core.app_config import get_app_metadata, openapi_overrides
from .core.docs import ocean_professional_openapi
from .core.errors import setup_exception_handlers

# Initialize FastAPI app with metadata
metadata = get_app_metadata()
app = FastAPI(
    title=metadata["title"],
    description=metadata["description"],
    version=metadata["version"],
    contact=metadata["contact"],
    license_info=metadata["license_info"],
    terms_of_service=metadata["terms_of_service"],
    openapi_tags=metadata["openapi_tags"],
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For demo; restrict in production via env
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(tracks.router, prefix="/api/tracks", tags=["Tracks"])
app.include_router(playback.router, prefix="/api/playback", tags=["Playback"])
app.include_router(glimpses.router, prefix="/api/glimpses", tags=["Video Glimpses"])

# Exception handlers
setup_exception_handlers(app)

# Health check
@app.get("/", summary="Health Check", tags=["System"])
# PUBLIC_INTERFACE
def health_check():
    """Basic system health check endpoint."""
    return {"status": "ok", "service": metadata["title"], "version": metadata["version"]}

# WebSocket usage helper route for docs discoverability
@app.get(
    "/docs/websocket",
    summary="WebSocket Usage",
    tags=["System"],
    description=(
        "This project currently serves HTTP endpoints only. "
        "If real-time playback sync is later added, WebSocket docs will appear here."
    ),
)
# PUBLIC_INTERFACE
def websocket_docs():
    """Provide WebSocket usage notes if/when real-time endpoints are added."""
    return {
        "websocket": "No WebSocket endpoints currently. Future real-time features will be documented here."
    }

# Apply OpenAPI and Swagger UI theming customizations
openapi_overrides(app)
app.openapi = ocean_professional_openapi(app)
