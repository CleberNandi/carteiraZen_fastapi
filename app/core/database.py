from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

DATABASE_URL = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)


def mask_db_url(url: str) -> str:
    """Remove senha da URL para exibir no log."""
    if "@" in url and "://" in url:
        prefix, rest = url.split("://", 1)
        if "@" in rest and ":" in rest.split("@")[0]:
            user, rest_after_user = rest.split("@", 1)
            user_no_pass = user.split(":")[0]
            return f"{prefix}://{user_no_pass}:***@{rest_after_user}"
    return url


print(f"🔹 DATABASE_URL database: {mask_db_url(DATABASE_URL)}")

# Async Engine
engine = create_async_engine(DATABASE_URL, echo=False)

# Async Session
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# Base para models
Base = declarative_base()


# Dependency para FastAPI
async def get_db() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session
