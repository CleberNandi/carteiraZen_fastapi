# main.py
from fastapi import FastAPI

from app.core.config import config
from app.core.lifespan import lifespan
from app.core.openapi import register_openapi_export
from app.core.routes import register_routers

app = FastAPI(
    title=getattr(config, "PROJECT_NAME", "No Project Name"),
    version=getattr(config, "VERSION", "0.0.1"),
    docs_url=None
    if config.ENV in ("prod", "production")
    else f"/{config.BASE_URL}/docs",
    redoc_url=None
    if config.ENV in ("prod", "production")
    else f"/{config.BASE_URL}/redoc",
    openapi_url=None
    if config.ENV in ("prod", "production")
    else f"/{config.BASE_URL}/openapi",
    lifespan=lifespan,
)

register_routers(app)
register_openapi_export(app)
