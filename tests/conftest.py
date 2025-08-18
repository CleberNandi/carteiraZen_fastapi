# conftest.py
import asyncio

from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db

# Imports do seu projeto baseado na estrutura mostrada
from app.main import app

# URL do banco de teste (SQLite em memória)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Engine de teste
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,  # Mude para True se quiser ver as queries SQL
)

TestSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Sessão do banco de dados para testes"""
    # Cria as tabelas
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Fornece a sessão
    async with TestSessionLocal() as session:
        yield session

    # Limpa as tabelas
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession):
    """Cliente HTTP assíncrono para testes"""

    # Override da dependência do banco
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Cliente assíncrono com transport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Limpa os overrides após o teste
    app.dependency_overrides.clear()


# Configuração para pytest-asyncio
@pytest.fixture(scope="session")
def event_loop():
    """Cria um loop de eventos para toda a sessão de testes"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()
