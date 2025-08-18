from httpx import AsyncClient
import pytest

# Marcar a classe como assíncrona
pytestmark = pytest.mark.asyncio


class TestAuth:
    """Testes para autenticação"""

    async def test_register_user(self, client: AsyncClient):
        """Testa registro de usuário"""
        user_data = {
            "email": "teste@example.com",
            "password": "MinhaSenh@123",
            "name": "Usuario Teste",  # Ajuste conforme seu schema
        }
        response = await client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code in [200, 201]  # Aceita ambos
        data = response.json()
        assert data["email"] == user_data["email"]
        return data

    async def test_login_success(self, client: AsyncClient):
        """Testa login com sucesso"""
        # Primeiro registra o usuário
        await self.test_register_user(client)

        # Agora faz o login
        login_data = {"email": "teste@example.com", "password": "MinhaSenh@123"}
        response = await client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Testa login com credenciais inválidas"""
        # Registra usuário primeiro
        await self.test_register_user(client)

        # Tenta login com senha errada
        login_data = {"email": "teste@example.com", "password": "SenhaErrada"}
        response = await client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    async def test_login_user_not_found(self, client: AsyncClient):
        """Testa login com usuário inexistente"""
        login_data = {"email": "inexistente@example.com", "password": "MinhaSenh@123"}
        response = await client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data


# Teste standalone (fora da classe)
async def test_standalone_login(client: AsyncClient):
    """Exemplo de teste standalone"""
    # Registra usuário
    user_data = {
        "email": "standalone@example.com",
        "password": "MinhaSenh@123",
        "name": "Usuario Standalone",
    }
    register_response = await client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code in [200, 201]

    # Faz login
    login_data = {"email": "standalone@example.com", "password": "MinhaSenh@123"}
    login_response = await client.post("/api/v1/auth/login", json=login_data)
    assert login_response.status_code == 200
    data = login_response.json()
    assert "access_token" in data
