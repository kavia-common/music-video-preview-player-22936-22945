from typing import Callable
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

def ocean_professional_openapi(app: FastAPI) -> Callable[[], dict]:
    """
    Return a callable that produces an OpenAPI schema with custom theming notes.
    """
    # PUBLIC_INTERFACE
    def _openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        # Provide a helpful tag order and UI hints
        openapi_schema["x-docs"] = {
            "theme": "Ocean Professional",
            "palette": {
                "primary": "#2563EB",
                "secondary": "#F59E0B",
                "error": "#EF4444",
                "surface": "#ffffff",
                "background": "#f9fafb",
                "text": "#111827",
            },
        }
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    return _openapi
