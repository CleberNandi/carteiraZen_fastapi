# tests/fixtures/cartao_fixtures.py

import pytest

from app.schemas.cartao import CartaoCreate, CartaoRead


@pytest.fixture
def make_fake_cartao_create():
    return CartaoCreate(
        numero="1234567890123456",
        descricao="Cartão de Teste",
        bandeira="VISA",
        limite_cents=500000,
        dia_fechamento=10,
        dias_vencimento=15,
        cor="#344534",
        conta_id=1,
    )


@pytest.fixture
def make_fake_cartao_update():
    return CartaoRead(
        id=1,
        numero="1234567890123456",
        descricao="Cartão de Teste Atualizado",
        bandeira="Visa",
        limite_cents=500000,
        dia_fechamento=10,
        dias_vencimento=15,
        cor="azul",
        conta_id=1,
    )
