from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base, engine
from seeds.seed_all import run_all_seeds


def import_all_models() -> None:
    from app.models.usuario import Usuario  # type: ignore # noqa: F401, I001
    from app.models.categoria import Categoria  # type: ignore # noqa: F401
    from app.models.orcamento import Orcamento  # type: ignore # noqa: F401
    from app.models.fatura import Fatura  # type: ignore # noqa: F401
    from app.models.fatura import FaturaPagamento  # type: ignore # noqa: F401
    from app.models.cartao import Cartao  # type: ignore # noqa: F401
    from app.models.conta import Conta  # type: ignore # noqa: F401
    from app.models.sub_categoria import SubCategoria  # type: ignore # noqa: F401
    from app.models.transacao import Transacao  # type: ignore # noqa: F401
    from app.models.transacao_parcela import TransacaoParcela  # type: ignore # noqa: F401
    from app.models.auth_session import AuthSession  # type: ignore # noqa: F401
    from app.models.backup_code import BackupCode  # type: ignore # noqa: F401
    from app.models.auditoria import Auditoria  # type: ignore # noqa: F401
    from app.models.banco import Banco  # type: ignore # noqa: F401
    from app.models.login_attempt import LoginAttempt  # type: ignore # noqa: F401
    from app.models.nfce import NFCe  # type: ignore # noqa: F401
    from app.models.nfce_itens import NFCeItens  # type: ignore # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    try:
        # 1. Criar tabelas
        async with engine.begin() as conn:
            import_all_models()
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database initialized")

        # 2. Rodar todos os seeds
        async with AsyncSession(engine) as session:
            await run_all_seeds(session)

        yield
    finally:
        # Shutdown
        await engine.dispose()
        print("🔒 Engine disposed")
