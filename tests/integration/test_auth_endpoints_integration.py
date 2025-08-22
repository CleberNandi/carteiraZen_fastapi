from httpx import AsyncClient
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.usuario import Usuario


@pytest.mark.asyncio
async def test_register_endpoint(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "nome": "User Test",
            "email": "usertest@example.com",
            "password": "Senha@123",
        },
    )

    assert response.status_code == 200
    body: dict[str, str | int] = response.json()
    assert "user_id" in body
    assert body["user_id"] == 1


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "usertest@example.com", "password": "wrongpassword"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, db_session: AsyncSession) -> None:
    # Primeiro registra o usuário
    user_data: dict[str, str] = {
        "nome": "User Success",
        "email": "success@example.com",
        "password": "Senha@123",
    }
    await client.post("/api/v1/auth/register", json=user_data)

    # Marcar usuário como verificado
    user = await db_session.execute(
        select(Usuario).where(Usuario.email == user_data["email"])
    )
    user = user.scalar_one()
    user.is_verified = True
    await db_session.commit()

    # Faz login
    login_data = {"email": "success@example.com", "password": "Senha@123"}
    response = await client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == 200
    data: dict[str, str | int | bool] = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
