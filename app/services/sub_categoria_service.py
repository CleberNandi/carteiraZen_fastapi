from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.sub_categoria import SubCategoria
from app.schemas.sub_categoria import SubCategoriaCreate, SubCategoriaRead

class SubCategoriaService:
    @staticmethod
    async def create(db: AsyncSession, sub_in: SubCategoriaCreate) -> SubCategoriaRead:
        sub = SubCategoria(**sub_in.model_dump())
        db.add(sub)
        await db.commit()
        await db.refresh(sub)
        return SubCategoriaRead.from_orm(sub)

    @staticmethod
    async def get(db: AsyncSession, sub_id: int) -> SubCategoriaRead | None:
        result = await db.execute(select(SubCategoria).where(SubCategoria.id == sub_id))
        sub = result.scalar_one_or_none()
        if sub:
            return SubCategoriaRead.from_orm(sub)
        return None

    @staticmethod
    async def list(db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(select(SubCategoria).offset(skip).limit(limit))
        return [SubCategoriaRead.from_orm(s) for s in result.scalars().all()]

    @staticmethod
    async def update(db: AsyncSession, sub_id: int, data: dict) -> SubCategoriaRead | None:
        result = await db.execute(select(SubCategoria).where(SubCategoria.id == sub_id))
        sub = result.scalar_one_or_none()
        if not sub:
            return None
        for key, value in data.items():
            setattr(sub, key, value)
        await db.commit()
        await db.refresh(sub)
        return SubCategoriaRead.from_orm(sub)

    @staticmethod
    async def delete(db: AsyncSession, sub_id: int) -> bool:
        result = await db.execute(select(SubCategoria).where(SubCategoria.id == sub_id))
        sub = result.scalar_one_or_none()
        if not sub:
            return False
        await db.delete(sub)
        await db.commit()
        return True
