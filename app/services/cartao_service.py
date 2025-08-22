from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.cartao import Cartao
from app.models.usuario import Usuario
from app.schemas.cartao import CartaoCreate, CartaoRead


class CartaoService:
    @staticmethod
    async def create(
        db: AsyncSession, cartao_in: CartaoCreate, current_user_id: int
    ) -> CartaoRead:
        cartao = Cartao(**cartao_in.model_dump(), usuario_id=current_user_id)
        db.add(cartao)
        await db.commit()
        await db.refresh(cartao)
        return CartaoRead.model_validate(cartao)

    @staticmethod
    async def get(
        db: AsyncSession, cartao_id: int, current_user: Usuario
    ) -> CartaoRead | None:
        result = await db.execute(
            select(Cartao).where(
                Cartao.id == cartao_id, Cartao.usuario_id == current_user.id
            )
        )
        cartao = result.scalar_one_or_none()
        if cartao:
            return CartaoRead.model_validate(cartao)
        return None

    @staticmethod
    async def list(
        db: AsyncSession, current_user: Usuario, skip: int = 0, limit: int = 100
    ) -> list[CartaoRead]:
        result = await db.execute(
            select(Cartao)
            .where(Cartao.usuario_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        return [CartaoRead.model_validate(c) for c in result.scalars().all()]

    @staticmethod
    async def update(
        db: AsyncSession, cartao_id: int, data: dict[str, str], current_user: Usuario
    ) -> CartaoRead | None:
        result = await db.execute(
            select(Cartao).where(
                Cartao.id == cartao_id, Cartao.usuario_id == current_user.id
            )
        )
        cartao = result.scalar_one_or_none()
        if not cartao:
            return None
        for key, value in data.items():
            setattr(cartao, key, value)
        await db.commit()
        await db.refresh(cartao)
        return CartaoRead.model_validate(cartao)

    @staticmethod
    async def delete(db: AsyncSession, cartao_id: int, current_user: Usuario) -> bool:
        result = await db.execute(
            select(Cartao).where(
                Cartao.id == cartao_id, Cartao.usuario_id == current_user.id
            )
        )
        cartao = result.scalar_one_or_none()
        if not cartao:
            return False
        await db.delete(cartao)
        await db.commit()
        return True
