from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.transacao import Transacao
from app.schemas.transacao import TransacaoCreate, TransacaoRead


class TransacaoService:
    @staticmethod
    async def create(db: AsyncSession, transacao_in: TransacaoCreate) -> TransacaoRead:
        transacao = Transacao(**transacao_in.model_dump())
        db.add(transacao)
        await db.commit()
        await db.refresh(transacao)
        return TransacaoRead.model_validate(transacao)

    @staticmethod
    async def get(db: AsyncSession, transacao_id: int) -> TransacaoRead | None:
        result = await db.execute(select(Transacao).where(Transacao.id == transacao_id))
        transacao = result.scalar_one_or_none()
        if transacao:
            return TransacaoRead.model_validate(transacao)
        return None

    @staticmethod
    async def list(
        db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[TransacaoRead]:
        result = await db.execute(select(Transacao).offset(skip).limit(limit))
        return [TransacaoRead.model_validate(t) for t in result.scalars().all()]

    @staticmethod
    async def update(
        db: AsyncSession, transacao_id: int, data: dict[str, str]
    ) -> TransacaoRead | None:
        result = await db.execute(select(Transacao).where(Transacao.id == transacao_id))
        transacao = result.scalar_one_or_none()
        if not transacao:
            return None
        for key, value in data.items():
            setattr(transacao, key, value)
        await db.commit()
        await db.refresh(transacao)
        return TransacaoRead.model_validate(transacao)

    @staticmethod
    async def delete(db: AsyncSession, transacao_id: int) -> bool:
        result = await db.execute(select(Transacao).where(Transacao.id == transacao_id))
        transacao = result.scalar_one_or_none()
        if not transacao:
            return False
        await db.delete(transacao)
        await db.commit()
        return True
