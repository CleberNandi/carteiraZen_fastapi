# tests/unit/test_cartoes_router.py
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
import pytest
from schemas.cartao import CartaoCreate
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.cartoes import router
from app.models.usuario import Usuario

pytestmark = pytest.mark.asyncio


async def test_create_cartao_success(
    db_session: AsyncSession, make_fake_cartao_create: CartaoCreate
):
    fake_user = Usuario(
        id=1,
        nome="Teste",
        email="teste@email.com",
        password_hashed="hashed_password",  # noqa: S106
        # adicione outros campos obrigatórios do seu model
    )
    with patch(
        "app.api.v1.endpoints.cartoes.router.CartaoService.create",
        new=AsyncMock(return_value=make_fake_cartao_create),
    ):
        result = await router.create_cartao(
            cartao_in=make_fake_cartao_create, db=db_session, current_user=fake_user
        )
        assert result.numero == "1234567890123456"


async def test_get_cartao_found(
    db_session: AsyncSession, make_fake_cartao_create: CartaoCreate
):
    with patch(
        "app.api.v1.endpoints.cartoes.router.CartaoService.get",
        new=AsyncMock(return_value=make_fake_cartao_create),
    ):
        result = await router.get_cartao(cartao_id=1, db=db_session)
        assert result.bandeira == "VISA"


async def test_get_cartao_not_found(
    db_session: AsyncSession, make_fake_cartao_create: CartaoCreate
):
    with patch(
        "app.api.v1.endpoints.cartoes.router.CartaoService.get",
        new=AsyncMock(return_value=None),
    ):
        with pytest.raises(HTTPException) as exc:
            await router.get_cartao(cartao_id=999, db=db_session)
        assert exc.value.status_code == 404


async def test_list_cartoes(db_session: AsyncSession):
    fake_list = [{"id": 1}, {"id": 2}]
    with patch(
        "app.api.v1.endpoints.cartoes.router.CartaoService.list",
        new=AsyncMock(return_value=fake_list),
    ):
        result = await router.list_cartoes(skip=0, limit=10, db=db_session)
        assert len(result) == 2


async def test_update_cartao_success(
    db_session: AsyncSession,
    make_fake_cartao_create: CartaoCreate,
    make_fake_cartao_update: CartaoCreate,
):
    with patch(
        "app.api.v1.endpoints.cartoes.router.CartaoService.update",
        new=AsyncMock(return_value=make_fake_cartao_update),
    ):
        result = await router.update_cartao(
            cartao_id=1, data=make_fake_cartao_create, db=db_session
        )
        assert result.descricao == "Cartão de Teste Atualizado"


async def test_update_cartao_not_found(
    db_session: AsyncSession, make_fake_cartao_create: CartaoCreate
):
    with (
        patch(
            "app.api.v1.endpoints.cartoes.router.CartaoService.update",
            new=AsyncMock(return_value=None),
        ),
        pytest.raises(HTTPException),
    ):
        await router.update_cartao(
            cartao_id=999, data=make_fake_cartao_create, db=db_session
        )


async def test_delete_cartao_success(db_session: AsyncSession):
    with patch(
        "app.api.v1.endpoints.cartoes.router.CartaoService.delete",
        new=AsyncMock(return_value=True),
    ):
        result = await router.delete_cartao(cartao_id=1, db=db_session)
        assert result == {"ok": True}


async def test_delete_cartao_not_found(db_session: AsyncSession):
    with (
        patch(
            "app.api.v1.endpoints.cartoes.router.CartaoService.delete",
            new=AsyncMock(return_value=False),
        ),
        pytest.raises(HTTPException),
    ):
        await router.delete_cartao(cartao_id=999, db=db_session)
