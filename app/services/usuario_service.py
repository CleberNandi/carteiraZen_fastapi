from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioRead


class UsuarioService:
    @staticmethod
    async def create(db: AsyncSession, usuario_in: UsuarioCreate) -> UsuarioRead:
        usuario = Usuario(**usuario_in.model_dump())
        db.add(usuario)
        await db.commit()
        await db.refresh(usuario)
        return UsuarioRead.model_validate(usuario)

    @staticmethod
    async def get(db: AsyncSession, usuario_id: int) -> UsuarioRead | None:
        result = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
        usuario = result.scalar_one_or_none()
        if usuario:
            return UsuarioRead.model_validate(usuario)
        return None

    @staticmethod
    async def list(
        db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[UsuarioRead]:
        result = await db.execute(select(Usuario).offset(skip).limit(limit))
        return [UsuarioRead.model_validate(u) for u in result.scalars().all()]

    @staticmethod
    async def update(
        db: AsyncSession, usuario_id: int, data: dict[str, str]
    ) -> UsuarioRead | None:
        result = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
        usuario = result.scalar_one_or_none()
        if not usuario:
            return None
        for key, value in data.items():
            setattr(usuario, key, value)
        await db.commit()
        await db.refresh(usuario)
        return UsuarioRead.model_validate(usuario)

    @staticmethod
    async def delete(db: AsyncSession, usuario_id: int) -> bool:
        result = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
        usuario = result.scalar_one_or_none()
        if not usuario:
            return False
        await db.delete(usuario)
        await db.commit()
        return True
