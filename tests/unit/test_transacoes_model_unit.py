from datetime import date

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transacao import Transacao


@pytest.mark.asyncio
async def test_criar_transacao(db_session: AsyncSession):
    nova = Transacao(
        tipo="entrada",
        valor_cents=1000,
        data_vencimento=date(2025, 8, 15),
        data_lancamento=date(2025, 8, 15),
        data_efetivacao=date(2025, 8, 15),
        cor="#FF0000",
        usuario_id=1,
    )
    db_session.add(nova)
    await db_session.commit()

    result = await db_session.get(Transacao, nova.id)
    assert result is not None
    assert result.valor_cents == 1000
