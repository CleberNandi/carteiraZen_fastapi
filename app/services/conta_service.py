from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.conta import Conta
from app.schemas.conta import ContaCreate, ContaRead

class ContaService:
    @staticmethod
    async def create(db: AsyncSession, conta_in: ContaCreate) -> ContaRead:
        conta = Conta(**conta_in.model_dump())
        db.add(conta)
        await db.commit()
        await db.refresh(conta)
        return ContaRead.from_orm(conta)

    @staticmethod
    async def get(db: AsyncSession, conta_id: int) -> ContaRead | None:
        result = await db.execute(select(Conta).where(Conta.id == conta_id))
        conta = result.scalar_one_or_none()
        if conta:
            return ContaRead.from_orm(conta)
        return None

    @staticmethod
    async def list(db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(select(Conta).offset(skip).limit(limit))
        return [ContaRead.from_orm(c) for c in result.scalars().all()]

    @staticmethod
    async def update(db: AsyncSession, conta_id: int, data: dict) -> ContaRead | None:
        result = await db.execute(select(Conta).where(Conta.id == conta_id))
        conta = result.scalar_one_or_none()
        if not conta:
            return None
        for key, value in data.items():
            setattr(conta, key, value)
        await db.commit()
        await db.refresh(conta)
        return ContaRead.from_orm(conta)

    @staticmethod
    async def delete(db: AsyncSession, conta_id: int) -> bool:
        result = await db.execute(select(Conta).where(Conta.id == conta_id))
        conta = result.scalar_one_or_none()
        if not conta:
            return False
        await db.delete(conta)
        await db.commit()
        return True
