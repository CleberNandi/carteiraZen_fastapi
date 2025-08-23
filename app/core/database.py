from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

# Async Engine
engine = create_async_engine(DATABASE_URL, echo=False)

# Async Session
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# Base para models
Base = declarative_base()


# Dependency para FastAPI
async def get_async_db() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session
