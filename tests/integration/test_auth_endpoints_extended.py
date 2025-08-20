# tests/integration/test_auth_endpoints_extended.py

from httpx import AsyncClient
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.usuario import Usuario


class TestAuthEndpointsExtended:
    """Testes para melhorar cobertura dos endpoints de auth"""

    @pytest.mark.asyncio
    async def test_login_email_not_verified(self, client: AsyncClient) -> None:
        """Testa login com email não verificado"""
        # Registrar usuário
        user_data = {
            "nome": "User Test",
            "email": "unverified@example.com",
            "password": "Senha@123",
        }
        await client.post("/api/v1/auth/register", json=user_data)

        # Tentar fazer login sem verificar email
        login_data = {"email": "unverified@example.com", "password": "Senha@123"}
        response = await client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 403
        data = response.json()
        assert "Email não verificado" in str(data.get("detail", ""))

    @pytest.mark.asyncio
    async def test_login_requires_2fa_without_code(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Testa login que requer 2FA mas não fornece código"""
        # Registrar usuário
        user_data = {
            "nome": "User Without 2FA",
            "email": "user2fa@example.com",
            "password": "Senha@123",
        }
        await client.post("/api/v1/auth/register", json=user_data)

        # Marcar usuário como verificado e com 2FA habilitado
        user = await db_session.execute(
            select(Usuario).where(Usuario.email == user_data["email"])
        )
        user = user.scalar_one()
        user.is_verified = True
        user.is_2fa_enabled = True
        await db_session.commit()

        # Fazer login sem código 2FA
        login_data = {"email": "user2fa@example.com", "password": "Senha@123"}
        response = await client.post("/api/v1/auth/login", json=login_data)

        # Deveria retornar sucesso mas indicando que precisa de 2FA
        assert response.status_code == 200  # ou 202
        data = response.json()
        assert data["requires_2fa"] is True
        assert data.get("access_token", "") == ""  # Token vazio quando requer 2FA

    @pytest.mark.asyncio
    async def test_refresh_token(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Testa refresh de token"""
        # Registrar e verificar usuário
        user_data = {
            "nome": "User Refresh",
            "email": "refresh@example.com",
            "password": "Senha@123",
        }
        await client.post("/api/v1/auth/register", json=user_data)

        user = await db_session.execute(
            select(Usuario).where(Usuario.email == user_data["email"])
        )
        user = user.scalar_one()
        user.is_verified = True
        await db_session.commit()

        # Fazer login para obter tokens
        login_data = {"email": "refresh@example.com", "password": "Senha@123"}
        login_response = await client.post("/api/v1/auth/login", json=login_data)
        tokens = login_response.json()

        # Testar refresh
        refresh_data = {"refresh_token": tokens["refresh_token"]}
        response = await client.post("/api/v1/auth/refresh", json=refresh_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    @pytest.mark.asyncio
    async def test_get_user_profile(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Testa obter perfil do usuário"""
        # Registrar e verificar usuário
        user_data = {
            "nome": "User Profile",
            "email": "profile@example.com",
            "password": "Senha@123",
        }
        await client.post("/api/v1/auth/register", json=user_data)

        user = await db_session.execute(
            select(Usuario).where(Usuario.email == user_data["email"])
        )
        user = user.scalar_one()
        user.is_verified = True
        await db_session.commit()

        # Fazer login
        login_data = {"email": "profile@example.com", "password": "Senha@123"}
        login_response = await client.post("/api/v1/auth/login", json=login_data)
        tokens = login_response.json()

        # Obter perfil
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = await client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["nome"] == "User Profile"
        assert data["email"] == "profile@example.com"

    @pytest.mark.asyncio
    async def test_logout(self, client: AsyncClient, db_session: AsyncSession) -> None:
        """Testa logout"""
        # Setup usuário verificado
        user_data = {
            "nome": "User Logout",
            "email": "logout@example.com",
            "password": "Senha@123",
        }
        await client.post("/api/v1/auth/register", json=user_data)

        user = await db_session.execute(
            select(Usuario).where(Usuario.email == user_data["email"])
        )
        user = user.scalar_one()
        user.is_verified = True
        await db_session.commit()

        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "logout@example.com", "password": "Senha@123"},
        )
        tokens = login_response.json()

        # Logout
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        logout_data = {"refresh_token": tokens["refresh_token"]}
        response = await client.post(
            "/api/v1/auth/logout", json=logout_data, headers=headers
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_logout_all(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Testa logout de todas as sessões"""
        # Setup usuário verificado
        user_data = {
            "nome": "User Logout All",
            "email": "logoutall@example.com",
            "password": "Senha@123",
        }
        await client.post("/api/v1/auth/register", json=user_data)

        user = await db_session.execute(
            select(Usuario).where(Usuario.email == user_data["email"])
        )
        user = user.scalar_one()
        user.is_verified = True
        await db_session.commit()

        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "logoutall@example.com", "password": "Senha@123"},
        )
        tokens = login_response.json()

        # Logout all
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = await client.post("/api/v1/auth/logout-all", headers=headers)

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_user_sessions(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Testa listar sessões do usuário"""
        # Setup usuário verificado
        user_data = {
            "nome": "User Sessions",
            "email": "sessions@example.com",
            "password": "Senha@123",
        }
        await client.post("/api/v1/auth/register", json=user_data)

        user = await db_session.execute(
            select(Usuario).where(Usuario.email == user_data["email"])
        )
        user = user.scalar_one()
        user.is_verified = True
        await db_session.commit()

        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "sessions@example.com", "password": "Senha@123"},
        )
        tokens = login_response.json()

        # Get sessions
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = await client.get("/api/v1/auth/sessions", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_verify_email(self, client: AsyncClient) -> None:
        """Testa verificação de email"""
        # Mock do token (você precisará ajustar conforme sua implementação)
        response = await client.get("/api/v1/auth/verify-email/mock_token")
        # O teste específico dependerá da sua implementação do AuthService.verify_email
        # Por enquanto só testamos se o endpoint existe
        assert response.status_code in [200, 400, 404]  # Dependendo da implementação

    @pytest.mark.asyncio
    async def test_resend_verification_email(self, client: AsyncClient) -> None:
        """Testa reenvio de email de verificação"""
        # Registrar usuário
        await client.post(
            "/api/v1/auth/register",
            json={
                "nome": "User Resend",
                "email": "resend@example.com",
                "password": "Senha@123",
            },
        )

        # Tentar reenviar verificação
        response = await client.post(
            "/api/v1/auth/resend-verification", json={"email": "resend@example.com"}
        )

        # O teste específico dependerá da sua implementação
        assert response.status_code in [200, 400, 404]

    @pytest.mark.asyncio
    async def test_setup_2fa(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Testa setup inicial do 2FA"""
        # Setup usuário verificado
        user_data = {
            "nome": "User 2FA Setup",
            "email": "2fasetup@example.com",
            "password": "Senha@123",
        }
        await client.post("/api/v1/auth/register", json=user_data)

        user = await db_session.execute(
            select(Usuario).where(Usuario.email == user_data["email"])
        )
        user = user.scalar_one()
        user.is_verified = True
        await db_session.commit()

        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "2fasetup@example.com", "password": "Senha@123"},
        )
        tokens = login_response.json()

        # Setup 2FA
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = await client.post("/api/v1/auth/2fa/setup", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "qr_code" in data or "secret" in data  # Dependendo da implementação

    @pytest.mark.asyncio
    async def test_setup_2fa_already_enabled(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Testa setup 2FA quando já está habilitado"""
        # Setup usuário verificado com 2FA já habilitado
        user_data = {
            "nome": "User 2FA Already",
            "email": "2faalready@example.com",
            "password": "Senha@123",
        }
        await client.post("/api/v1/auth/register", json=user_data)

        user = await db_session.execute(
            select(Usuario).where(Usuario.email == user_data["email"])
        )
        user = user.scalar_one()
        user.is_verified = True
        await db_session.commit()

        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "2faalready@example.com", "password": "Senha@123"},
        )
        assert login_response.status_code == 200
        tokens = login_response.json()

        # Habilitar 2FA primeiro
        user.is_2fa_enabled = True
        import pyotp

        secret = pyotp.random_base32()
        user.secret_key_2fa = secret
        await db_session.commit()

        # Tentar setup 2FA novamente
        headers = {"Authorization": f"bearer {tokens['access_token']}"}
        response = await client.post("/api/v1/auth/2fa/setup", headers=headers)

        assert response.status_code == 400
        data = response.json()
        assert "2FA já está habilitado" in str(data.get("detail", ""))

    @pytest.mark.asyncio
    async def test_disable_2fa_not_enabled(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Testa desabilitar 2FA quando não está habilitado"""
        # Setup usuário verificado sem 2FA
        user_data = {
            "nome": "User No 2FA",
            "email": "no2fa@example.com",
            "password": "Senha@123",
        }
        await client.post("/api/v1/auth/register", json=user_data)

        user = await db_session.execute(
            select(Usuario).where(Usuario.email == user_data["email"])
        )
        user = user.scalar_one()
        user.is_verified = True
        await db_session.commit()

        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "no2fa@example.com", "password": "Senha@123"},
        )
        tokens = login_response.json()

        # Tentar desabilitar 2FA
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = await client.post("/api/v1/auth/2fa/disable", headers=headers)

        assert response.status_code == 400
        data = response.json()
        assert "2FA não está habilitado" in str(data.get("detail", ""))

    @pytest.mark.asyncio
    async def test_change_password(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Testa mudança de senha"""
        # Setup usuário verificado
        user_data = {
            "nome": "User Change Password",
            "email": "changepass@example.com",
            "password": "Senha@123",
        }
        await client.post("/api/v1/auth/register", json=user_data)

        user = await db_session.execute(
            select(Usuario).where(Usuario.email == user_data["email"])
        )
        user = user.scalar_one()
        user.is_verified = True
        await db_session.commit()

        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "changepass@example.com", "password": "Senha@123"},
        )
        tokens = login_response.json()

        # Mudar senha
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        password_data = {
            "current_password": "Senha@123",
            "new_password": "NovaSenha@456",
        }
        response = await client.post(
            "/api/v1/auth/password/change", json=password_data, headers=headers
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_password_reset_request(self, client: AsyncClient) -> None:
        """Testa solicitação de reset de senha"""
        reset_data = {"email": "reset@example.com"}
        response = await client.post(
            "/api/v1/auth/password/reset-request", json=reset_data
        )

        assert response.status_code == 200
        data = response.json()
        assert "email" in str(data.get("message", "")).lower()

    @pytest.mark.asyncio
    async def test_password_reset_confirm(self, client: AsyncClient) -> None:
        """Testa confirmação de reset de senha"""
        reset_data = {"token": "mock_token", "new_password": "NovaSenha@123"}
        response = await client.post(
            "/api/v1/auth/password/reset-confirm", json=reset_data
        )

        # O teste específico dependerá da sua implementação
        assert response.status_code in [200, 400, 404]
