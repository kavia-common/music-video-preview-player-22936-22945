from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

def setup_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers for consistent error payloads."""
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        # Allow FastAPI/HTTPExceptions to be handled by default mechanisms
        # Only catch generic Exceptions for a uniform error body
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": str(exc),
                "path": request.url.path,
            },
        )
