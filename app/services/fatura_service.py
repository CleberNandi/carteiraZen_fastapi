from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.fatura import Fatura
from app.schemas.fatura import FaturaCreate, FaturaRead

class FaturaService:
    @staticmethod
    async def create(db: AsyncSession, fatura_in: FaturaCreate) -> FaturaRead:
        fatura = Fatura(**fatura_in.model_dump())
        db.add(fatura)
        await db.commit()
        await db.refresh(fatura)
        return FaturaRead.from_orm(fatura)

    @staticmethod
    async def get(db: AsyncSession, fatura_id: int) -> FaturaRead | None:
        result = await db.execute(select(Fatura).where(Fatura.id == fatura_id))
        fatura = result.scalar_one_or_none()
        if fatura:
            return FaturaRead.from_orm(fatura)
        return None

    @staticmethod
    async def list(db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(select(Fatura).offset(skip).limit(limit))
        return [FaturaRead.from_orm(f) for f in result.scalars().all()]

    @staticmethod
    async def update(db: AsyncSession, fatura_id: int, data: dict) -> FaturaRead | None:
        result = await db.execute(select(Fatura).where(Fatura.id == fatura_id))
        fatura = result.scalar_one_or_none()
        if not fatura:
            return None
        for key, value in data.items():
            setattr(fatura, key, value)
        await db.commit()
        await db.refresh(fatura)
        return FaturaRead.from_orm(fatura)

    @staticmethod
    async def delete(db: AsyncSession, fatura_id: int) -> bool:
        result = await db.execute(select(Fatura).where(Fatura.id == fatura_id))
        fatura = result.scalar_one_or_none()
        if not fatura:
            return False
        await db.delete(fatura)
        await db.commit()
        return True
