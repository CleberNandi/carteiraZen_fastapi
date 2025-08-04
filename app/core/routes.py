# app/core/routes.py
from fastapi import FastAPI

from app.api.auditoria.v1.routers import router as auditoria_router
from app.api.auth.v1.routers import router as auth_router
from app.api.bancos.v1.routers import router as bancos_router
from app.api.cartoes.v1.routers import router as cartoes_router
from app.api.categorias.v1.routers import router as categorias_router
from app.api.contas.v1.routers import router as contas_correntes_router
from app.api.faturas.v1.routers import router as faturas_router
from app.api.nfce.v1.routers import router as nfce_router
from app.api.transacoes.v1.routers import router as transacoes_router
from app.api.users.v1.routers import router as users_router


def register_routers(app: FastAPI) -> None:
    app.include_router(users_router, prefix="/api/v1")
    app.include_router(bancos_router, prefix="/api/v1")
    app.include_router(auditoria_router, prefix="/api/v1")
    app.include_router(contas_correntes_router, prefix="/api/v1")
    app.include_router(cartoes_router, prefix="/api/v1")
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(categorias_router, prefix="/api/v1")
    app.include_router(faturas_router, prefix="/api/v1")
    app.include_router(transacoes_router, prefix="/api/v1")
    app.include_router(nfce_router, prefix="/api/v1")
