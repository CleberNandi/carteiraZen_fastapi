from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.cartao import Cartao
from app.schemas.cartao import CartaoCreate, CartaoRead

class CartaoService:
    @staticmethod
    async def create(db: AsyncSession, cartao_in: CartaoCreate) -> CartaoRead:
        cartao = Cartao(**cartao_in.model_dump())
        db.add(cartao)
        await db.commit()
        await db.refresh(cartao)
        return CartaoRead.from_orm(cartao)

    @staticmethod
    async def get(db: AsyncSession, cartao_id: int) -> CartaoRead | None:
        result = await db.execute(select(Cartao).where(Cartao.id == cartao_id))
        cartao = result.scalar_one_or_none()
        if cartao:
            return CartaoRead.from_orm(cartao)
        return None

    @staticmethod
    async def list(db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(select(Cartao).offset(skip).limit(limit))
        return [CartaoRead.from_orm(c) for c in result.scalars().all()]

    @staticmethod
    async def update(db: AsyncSession, cartao_id: int, data: dict) -> CartaoRead | None:
        result = await db.execute(select(Cartao).where(Cartao.id == cartao_id))
        cartao = result.scalar_one_or_none()
        if not cartao:
            return None
        for key, value in data.items():
            setattr(cartao, key, value)
        await db.commit()
        await db.refresh(cartao)
        return CartaoRead.from_orm(cartao)

    @staticmethod
    async def delete(db: AsyncSession, cartao_id: int) -> bool:
        result = await db.execute(select(Cartao).where(Cartao.id == cartao_id))
        cartao = result.scalar_one_or_none()
        if not cartao:
            return False
        await db.delete(cartao)
        await db.commit()
        return True
