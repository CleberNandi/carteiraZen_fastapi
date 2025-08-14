from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import importlib
import pkgutil
import uvicorn
from pyngrok import ngrok

from app.core.database import engine, Base
import app.routers as api_v1

# Lifespan para startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
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

# FastAPI app
app = FastAPI(title="Zenny API", version="1.0.0", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Função para incluir todos os routers dinamicamente
def include_all_routers(app, package):
    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        try:
            module = importlib.import_module(f"{package.__name__}.{module_name}.router")
            if hasattr(module, "router"):
                prefix = f"/api/v1/{module_name}"
                tags = [module_name.capitalize()]
                app.include_router(module.router, prefix=prefix, tags=tags)
        except ModuleNotFoundError:
            continue

include_all_routers(app, api_v1)

# Dev: ngrok
def run_ngrok(port=8000):
    public_url = ngrok.connect(port, bind_tls=True).public_url
    print(f"🚀 Ngrok HTTPS URL: {public_url}")

# Entry point
if __name__ == "__main__":
    port = 8000
    run_ngrok(port)
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
