import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import UserRegister
from app.services.auth_service import AuthService


@pytest.mark.asyncio
async def test_register_user(db_session: AsyncSession) -> None:
    user_data: UserRegister = UserRegister(
        nome="Teste",
        email="teste@example.com",
        password="Senha@123",  # noqa: S106
    )

    result: dict[str, str | int] = await AuthService.register_user(
        db_session, user_data, ip_address="127.0.0.1", user_agent="pytest"
    )

    assert "user_id" in result
    assert result["user_id"] == 1
