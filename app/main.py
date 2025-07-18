# main.py
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import config
from app.core.lifespan import lifespan
from app.core.openapi import register_openapi_export
from app.core.routes import register_routers
from app.handlers.http_errors import (
    validation_exception_handler,
)

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

app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "*",
    ],  # ou ["*"] para testar (não recomendado em produção)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_routers(app)
register_openapi_export(app)
