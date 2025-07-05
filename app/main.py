from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.agencias.v1.routers import router as agencias_router
from app.api.auditoria.v1.routers import router as auditoria_router
from app.api.auth.v1.routers import router as auth_router
from app.api.bancos.v1.routers import router as bancos_router
from app.api.cartoes.v1.routers import router as cartoes_router
from app.api.categorias.v1.routers import router as categorias_router
from app.api.contas_correntes.v1.routers import router as contas_correntes_router
from app.api.faturas.v1.routers import router as faturas_router
from app.api.transacoes.v1.routers import router as transacoes_router
from app.api.users.v1.routers import router as users_router
from app.core.config import config
from app.db.base import Base
from app.db.session import engine

# Adiciona o seed completo na inicialização
from app.scripts.seed_all import seed_all


# Lifespan tipado como AsyncGenerator[None] para compatibilidade total com FastAPI e mypy.
# Alguns linters podem sugerir omitir os argumentos, mas o padrão recomendado é mantê-los.
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    Base.metadata.create_all(bind=engine)
    seed_all()
    yield


app = FastAPI(
    title=getattr(config, "PROJECT_NAME", "No Project Name"),
    version=getattr(config, "VERSION", "0.0.1"),
    docs_url=f"/{config.BASE_URL}/docs",
    redoc_url=f"/{config.BASE_URL}/redoc",
    openapi_url=f"/{config.BASE_URL}/openapi",
    lifespan=lifespan,
)

if config.ENV in ("prod", "production"):
    app.docs_url = None
    app.redoc_url = None
    app.openapi_url = None

app.include_router(users_router, prefix="/api/v1")
app.include_router(bancos_router, prefix="/api/v1")
app.include_router(auditoria_router, prefix="/api/v1")
app.include_router(agencias_router, prefix="/api/v1")
app.include_router(contas_correntes_router, prefix="/api/v1")
app.include_router(cartoes_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(categorias_router, prefix="/api/v1")
app.include_router(faturas_router, prefix="/api/v1")
app.include_router(transacoes_router, prefix="/api/v1")
