import asyncio
import time
import uuid

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.usuario import Usuario


class TestUserManager:
    """Classe helper para gerenciar usuários nos testes"""

    @staticmethod
    def get_unique_email(base: str) -> str:
        """Gera email único para evitar conflitos"""
        timestamp = int(time.time() * 1000)
        unique_id = str(uuid.uuid4())[:8]
        return f"{base}_{timestamp}_{unique_id}@example.com"

    @staticmethod
    async def create_verified_user(
        client: AsyncClient,
        db_session: AsyncSession,
        base_name: str = "testuser",
        password: str = "Senha@123",  # noqa: S107
        *,
        enable_2fa: bool = False,
    ) -> tuple[str, Usuario] | None:
        """
        Cria um usuário verificado para testes.
        Retorna (email, user) ou None se falhar por rate limiting.
        """
        email = TestUserManager.get_unique_email(base_name)
        user_data = {
            "nome": f"Test User {base_name}",
            "email": email,
            "password": password,
        }

        # Tentar registrar usuário
        register_response = await client.post("/api/v1/auth/register", json=user_data)

        if register_response.status_code != 200:
            return None  # Rate limit ou outro erro

        # Aguardar um pouco para evitar problemas de timing
        await asyncio.sleep(0.1)

        # Buscar usuário no banco
        result = await db_session.execute(select(Usuario).where(Usuario.email == email))
        user = result.scalar_one_or_none()

        if user is None:
            return None  # Usuário não foi criado

        # Configurar usuário
        user.is_verified = True
        if enable_2fa:
            user.is_2fa_enabled = True
            user.totp_secret = "test_secret_for_testing"  # noqa: S105

        await db_session.commit()
        await db_session.refresh(user)

        return email, user

    @staticmethod
    async def login_user(
        client: AsyncClient, email: str, password: str = "Senha@123"
    ) -> dict[str, str] | None:  # noqa: S107
        """
        Faz login de um usuário.
        Retorna tokens ou None se falhar.
        """
        login_data = {"email": email, "password": password}
        login_response = await client.post("/api/v1/auth/login", json=login_data)

        if login_response.status_code != 200:
            return None

        return login_response.json()
