from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1 import endpoints
from app.config.config import settings
from app.db.session import Base, engine


# Lifespan tipado como AsyncGenerator[None] para compatibilidade total com FastAPI e mypy.
# Alguns linters podem sugerir omitir os argumentos, mas o padrão recomendado é mantê-los.
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=getattr(settings, "PROJECT_NAME", "No Project Name"),
    version=getattr(settings, "VERSION", "0.0.1"),
    docs_url=f"/{settings.BASE_URL}/docs",
    redoc_url=f"/{settings.BASE_URL}/redoc",
    openapi_url=f"/{settings.BASE_URL}/openapi",
    lifespan=lifespan,
)

if settings.ENV in ("prod", "production"):
    app.docs_url = None
    app.redoc_url = None
    app.openapi_url = None

app.include_router(endpoints.router, prefix="/api/v1")
