from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
import importlib
import os
import pkgutil
from types import ModuleType
from typing import TYPE_CHECKING, cast

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pyngrok import ngrok  # type: ignore
from slowapi import Limiter
from slowapi.util import get_remote_address
import uvicorn

from app.api.v1 import endpoints
from app.core.database import Base, engine
from app.core.middleware import SecurityMiddleware

if TYPE_CHECKING:
    from enum import Enum


# Lifespan para startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    try:
        # Startup: criar tabelas
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database initialized")
        yield
    finally:
        # Shutdown: fechar engine
        await engine.dispose()
        print("🔒 Engine disposed")


# Rate limiting global
limiter = Limiter(key_func=get_remote_address)

# FastAPI app
app = FastAPI(title="Zenny API", version="1.0.0", lifespan=lifespan)

# Rate limiting
app.state.limiter = limiter


# Middlewares
app.add_middleware(SecurityMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def include_all_routers(
    app: FastAPI, package: ModuleType, api_version: str = "v1"
) -> None:
    """
    Inclui todos os routers dinamicamente da estrutura app/api/{version}/endpoints/

    Args:
        app: FastAPI instance
        package: Módulo dos endpoints (app.api.v1.endpoints)
        api_version: Versão da API (default: v1)
    """
    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        try:
            module = importlib.import_module(f"{package.__name__}.{module_name}.router")
            if hasattr(module, "router"):
                prefix = f"/api/{api_version}/{module_name}"
                tags = cast("list[str | Enum]", [module_name.capitalize()])
                app.include_router(module.router, prefix=prefix, tags=tags)
                print(f"✅ Router incluído: {prefix}")  # Log para debug
        except ModuleNotFoundError as e:
            print(f"⚠️  Router não encontrado: {module_name} - {e}")
            continue


include_all_routers(app, endpoints)


def run_ngrok(port: int = 8000) -> None:
    public_url = ngrok.connect(port, bind_tls=True).public_url  # type: ignore
    print(f"🚀 Ngrok HTTPS URL: {public_url}")


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Zenny API v1.0 - Sistema de autenticação ativo"}


@app.get("/health")
async def health_check() -> dict[str, str | datetime]:
    return {"status": "healthy", "timestamp": datetime.now(UTC)}


# Entry point
if __name__ == "__main__":
    port = 8000
    if os.environ.get("RUN_MAIN") != "true":  # Evita rodar 2x no reload
        run_ngrok(port)
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)  # noqa: S104
