from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.banco import Banco
from app.schemas.banco import BancoCreate, BancoRead


class BancoService:
    @staticmethod
    async def create(db: AsyncSession, banco_in: BancoCreate) -> BancoRead:
        banco = Banco(**banco_in.model_dump())
        db.add(banco)
        await db.commit()
        await db.refresh(banco)
        return BancoRead.model_validate(banco)

    @staticmethod
    async def get(db: AsyncSession, banco_id: int) -> BancoRead | None:
        result = await db.execute(select(Banco).where(Banco.id == banco_id))
        banco = result.scalar_one_or_none()
        if banco:
            return BancoRead.model_validate(banco)
        return None

    @staticmethod
    async def list(
        db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[BancoRead]:
        result = await db.execute(select(Banco).offset(skip).limit(limit))
        return [BancoRead.model_validate(b) for b in result.scalars().all()]

    @staticmethod
    async def update(
        db: AsyncSession, banco_id: int, data: dict[str, str]
    ) -> BancoRead | None:
        result = await db.execute(select(Banco).where(Banco.id == banco_id))
        banco = result.scalar_one_or_none()
        if not banco:
            return None
        for key, value in data.items():
            setattr(banco, key, value)
        await db.commit()
        await db.refresh(banco)
        return BancoRead.model_validate(banco)

    @staticmethod
    async def delete(db: AsyncSession, banco_id: int) -> bool:
        result = await db.execute(select(Banco).where(Banco.id == banco_id))
        banco = result.scalar_one_or_none()
        if not banco:
            return False
        await db.delete(banco)
        await db.commit()
        return True
