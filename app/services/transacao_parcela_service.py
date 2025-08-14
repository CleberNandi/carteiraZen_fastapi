from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.transacao_parcela import TransacaoParcela
from app.schemas.transacao_parcela import TransacaoParcelaCreate, TransacaoParcelaRead


class TransacaoParcelaService:
    @staticmethod
    async def create(
        db: AsyncSession, parcela_in: TransacaoParcelaCreate
    ) -> TransacaoParcelaRead:
        parcela = TransacaoParcela(**parcela_in.model_dump())
        db.add(parcela)
        await db.commit()
        await db.refresh(parcela)
        return TransacaoParcelaRead.model_validate(parcela)

    @staticmethod
    async def get(db: AsyncSession, parcela_id: int) -> TransacaoParcelaRead | None:
        result = await db.execute(
            select(TransacaoParcela).where(TransacaoParcela.id == parcela_id)
        )
        parcela = result.scalar_one_or_none()
        if parcela:
            return TransacaoParcelaRead.model_validate(parcela)
        return None

    @staticmethod
    async def list(
        db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[TransacaoParcelaRead]:
        result = await db.execute(select(TransacaoParcela).offset(skip).limit(limit))
        return [TransacaoParcelaRead.model_validate(p) for p in result.scalars().all()]

    @staticmethod
    async def update(
        db: AsyncSession, parcela_id: int, data: dict[str, str]
    ) -> TransacaoParcelaRead | None:
        result = await db.execute(
            select(TransacaoParcela).where(TransacaoParcela.id == parcela_id)
        )
        parcela = result.scalar_one_or_none()
        if not parcela:
            return None
        for key, value in data.items():
            setattr(parcela, key, value)
        await db.commit()
        await db.refresh(parcela)
        return TransacaoParcelaRead.model_validate(parcela)

    @staticmethod
    async def delete(db: AsyncSession, parcela_id: int) -> bool:
        result = await db.execute(
            select(TransacaoParcela).where(TransacaoParcela.id == parcela_id)
        )
        parcela = result.scalar_one_or_none()
        if not parcela:
            return False
        await db.delete(parcela)
        await db.commit()
        return True
