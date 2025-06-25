from fastapi import FastAPI

from app.api.v1 import endpoints
from app.config.config import settings

app = FastAPI(
    title=getattr(settings, "PROJECT_NAME", "No Project Name"),
    version=getattr(settings, "VERSION", "0.0.1"),
    docs_url=f"/{settings.BASE_URL}/docs",
    redoc_url=f"/{settings.BASE_URL}/redoc",
    openapi_url=f"/{settings.BASE_URL}/openapi",
)

if settings.ENV in ("prod", "production"):
    app.docs_url = None
    app.redoc_url = None
    app.openapi_url = None

app.include_router(endpoints.router)
