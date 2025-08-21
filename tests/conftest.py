# tests/conftest.py
import asyncio
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_async_db
from app.main import app

pytest_plugins = [
    "tests.fixtures.users_fixtures",
    "tests.fixtures.categoria_fixtures",
]

# URL do banco de teste (SQLite em memória)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Engine de teste
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False, "isolation_level": None},
    poolclass=StaticPool,
    echo=False,
)

TestSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession]:
    """
    Sessão do banco de dados para testes.

    Cria todas as tabelas antes do teste e remove após.
    Garante isolamento entre testes.
    """
    # Criar todas as tabelas
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Fornecer sessão para o teste
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            # Rollback de qualquer transação pendente
            await session.rollback()

    # Limpar todas as tabelas após o teste
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession):
    """
    Cliente HTTP assíncrono para testes de integração.

    Sobrescreve a dependência do banco de dados para usar a sessão de teste.
    """

    async def override_get_db() -> AsyncGenerator[AsyncSession]:
        yield db_session

    # Sobrescrever dependência
    app.dependency_overrides[get_async_db] = override_get_db

    # Criar cliente HTTP
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        try:
            yield ac
        finally:
            # Limpar overrides
            app.dependency_overrides.clear()


# Configuração para pytest-asyncio
@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop

    # Fechar o loop após os testes
    if not loop.is_closed():
        loop.close()


@pytest.fixture(scope="session")
def test_app() -> FastAPI:
    """Instância da aplicação FastAPI para testes."""
    return app


# Fixtures auxiliares para configuração de testes
@pytest.fixture
def mock_settings():
    """Mock das configurações da aplicação."""
    from unittest.mock import MagicMock

    settings = MagicMock()
    settings.database_url = TEST_DATABASE_URL
    settings.secret_key = "test-secret-key"  # noqa: S105
    settings.algorithm = "HS256"
    settings.access_token_expire_minutes = 30
    settings.environment = "test"

    return settings


@pytest.fixture
def mock_current_user():
    """Mock de usuário autenticado para testes."""
    from unittest.mock import MagicMock

    from app.models.usuario import Usuario

    user = MagicMock(spec=Usuario)
    user.id = 1
    user.nome = "Test User"
    user.email = "test@example.com"
    user.is_verified = True
    user.is_active = True
    return user


@pytest.fixture
def mock_current_user_not_verified():
    """Mock de usuário autenticado para testes."""
    from unittest.mock import MagicMock

    from app.models.usuario import Usuario

    user = MagicMock(spec=Usuario)
    user.id = 1
    user.nome = "Test User"
    user.email = "test@example.com"
    user.is_active = True
    return user
