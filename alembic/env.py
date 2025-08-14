# app/alembic/env.py
import asyncio
import logging
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context
from app import models  # noqa: F401 - garante que Alembic veja todos os models
from app.core.config import settings
from app.core.database import Base

# Config Alembic
config = context.config
fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")

# Escolhe URL do banco
if settings.ENV_MODE == "test":
    DATABASE_URL = "sqlite+aiosqlite:///:memory:"
else:
    DATABASE_URL = str(settings.DATABASE_URL)

# Metadata alvo
target_metadata = Base.metadata


def mask_db_url(url: str) -> str:
    """Remove senha da URL para exibir no log."""
    if "@" in url and "://" in url:
        prefix, rest = url.split("://", 1)
        if "@" in rest and ":" in rest.split("@")[0]:
            user, rest_after_user = rest.split("@", 1)
            user_no_pass = user.split(":")[0]
            return f"{prefix}://{user_no_pass}:***@{rest_after_user}"
    return url


def validate_env_and_db():
    """Evita rodar migrations no banco errado."""
    is_sqlite = DATABASE_URL.startswith("sqlite")
    is_postgres = DATABASE_URL.startswith("postgres")

    if settings.ENV_MODE == "prod" and not is_postgres:
        raise RuntimeError("🚫 Produção só pode rodar migrations em PostgreSQL.")
    if settings.ENV_MODE == "test" and not is_sqlite:
        raise RuntimeError("🚫 Testes só podem rodar migrations em SQLite (in-memory).")


def run_migrations_offline() -> None:
    """Migrations no modo offline (sempre Postgres)."""
    validate_env_and_db()
    masked_url = mask_db_url(str(settings.DATABASE_URL))
    logger.info(
        f"[Alembic] Modo: OFFLINE | ENV_MODE: {settings.ENV_MODE} | Banco: {masked_url}"
    )

    context.configure(
        url=str(settings.DATABASE_URL),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Executa migrations com uma conexão já aberta."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Migrations no modo online (Postgres ou SQLite in-memory)."""
    validate_env_and_db()
    masked_url = mask_db_url(DATABASE_URL)
    logger.info(
        f"[Alembic] Modo: ONLINE | ENV_MODE: {settings.ENV_MODE} | Banco: {masked_url}"
    )

    connectable = create_async_engine(
        DATABASE_URL, poolclass=pool.NullPool, future=True
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
