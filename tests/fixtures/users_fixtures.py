from unittest.mock import MagicMock

from httpx import AsyncClient
import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.usuario import Usuario


@pytest.fixture
def mock_user() -> Usuario:
    user = MagicMock(spec=Usuario)
    user.id = 1
    user.nome = "Test User"
    user.email = "test@example.com"
    return user


@pytest.fixture
def another_mock_user() -> Usuario:
    user = MagicMock(spec=Usuario)
    user.id = 2
    user.nome = "Another User"
    user.email = "another@example.com"
    return user


@pytest_asyncio.fixture
async def authenticated_user(
    db_session: AsyncSession,
    client: AsyncClient,
    email: str = "teste@example.com",
    password: str = "Senha@123",  # noqa: S107
) -> dict[str, str]:
    """
    Cria um usuário de teste, marca como verificado e retorna um access token válido.
    Pode receber email e senha personalizados.
    """
    user_data = {
        "nome": "User Teste",
        "email": email,
        "password": password,
    }

    # Registrar via endpoint
    await client.post("/api/v1/auth/register", json=user_data)

    # Buscar usuário no banco e marcar como verificado
    result = await db_session.execute(select(Usuario).where(Usuario.email == email))
    user = result.scalar_one()
    user.is_verified = True
    await db_session.commit()

    # Fazer login e retornar token
    login_data = {"email": email, "password": password}
    login_response = await client.post("/api/v1/auth/login", json=login_data)
    tokens = login_response.json()
    access_token = tokens["access_token"]

    return {"Authorization": f"Bearer {access_token}"}
