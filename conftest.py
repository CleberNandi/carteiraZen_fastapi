# tests/conftest.py
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base

# Ajuste para testes
DATABASE_URL_TEST = "sqlite+aiosqlite:///:memory:"

# Cria engine global
engine_test = create_async_engine(
    DATABASE_URL_TEST,
    echo=True,
    future=True,
    connect_args={
        "check_same_thread": False
    },  # ⚡ permite usar mesma conexão em várias sessões
)
# Session async
AsyncSessionLocal = sessionmaker(
    bind=engine_test,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Fixture para criar o schema antes dos testes
@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine_test.dispose()


# Fixture para fornecer sessão por teste
@pytest_asyncio.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session
