# tests/conftest.py
import asyncio
from collections.abc import AsyncGenerator
import datetime
import sqlite3

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
    "tests.fixtures.cartao_fixtures",
]

# --- Adapters para Python 3.12 ---
sqlite3.register_adapter(datetime.date, lambda d: d.isoformat())
sqlite3.register_adapter(datetime.datetime, lambda dt: dt.isoformat(" "))
sqlite3.register_converter("DATE", lambda s: datetime.date.fromisoformat(s.decode()))
sqlite3.register_converter(
    "TIMESTAMP", lambda s: datetime.datetime.fromisoformat(s.decode())
)

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
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient]:
    async def override_get_db() -> AsyncGenerator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_async_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        try:
            yield ac
        finally:
            app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    if not loop.is_closed():
        loop.close()


@pytest.fixture(scope="session")
def test_app() -> FastAPI:
    return app


@pytest.fixture
def mock_settings():
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
    from unittest.mock import MagicMock

    from app.models.usuario import Usuario

    user = MagicMock(spec=Usuario)
    user.id = 1
    user.nome = "Test User"
    user.email = "test@example.com"
    user.is_active = True
    return user
