# app/core/openapi.py
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.core.config import config


def register_openapi_export(app: FastAPI) -> None:
    if config.ENV not in ("prod", "production"):

        @app.get("/openapi.json", tags=["OpenAPI"])
        def custom_openapi() -> JSONResponse:  # type: ignore
            return JSONResponse(app.openapi())
