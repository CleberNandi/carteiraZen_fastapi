from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.categoria import Categoria
from app.schemas.categoria import CategoriaCreate, CategoriaRead


class CategoriaService:
    @staticmethod
    async def create(db: AsyncSession, categoria_in: CategoriaCreate) -> CategoriaRead:
        categoria = Categoria(**categoria_in.model_dump())
        db.add(categoria)
        await db.commit()
        await db.refresh(categoria)
        return CategoriaRead.model_validate(categoria)

    @staticmethod
    async def get(db: AsyncSession, categoria_id: int) -> CategoriaRead | None:
        result = await db.execute(select(Categoria).where(Categoria.id == categoria_id))
        categoria = result.scalar_one_or_none()
        if categoria:
            return CategoriaRead.model_validate(categoria)
        return None

    @staticmethod
    async def list(
        db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[CategoriaRead]:
        result = await db.execute(select(Categoria).offset(skip).limit(limit))
        return [CategoriaRead.model_validate(c) for c in result.scalars().all()]

    @staticmethod
    async def update(
        db: AsyncSession, categoria_id: int, data: dict[str, str]
    ) -> CategoriaRead | None:
        result = await db.execute(select(Categoria).where(Categoria.id == categoria_id))
        categoria = result.scalar_one_or_none()
        if not categoria:
            return None
        for key, value in data.items():
            setattr(categoria, key, value)
        await db.commit()
        await db.refresh(categoria)
        return CategoriaRead.model_validate(categoria)

    @staticmethod
    async def delete(db: AsyncSession, categoria_id: int) -> bool:
        result = await db.execute(select(Categoria).where(Categoria.id == categoria_id))
        categoria = result.scalar_one_or_none()
        if not categoria:
            return False
        await db.delete(categoria)
        await db.commit()
        return True
