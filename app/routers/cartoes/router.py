from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.cartao import CartaoCreate, CartaoRead
from app.services.cartao_service import CartaoService

router = APIRouter()


@router.post("/", response_model=CartaoRead)
async def create_cartao(
    cartao_in: CartaoCreate, db: AsyncSession = Depends(get_db)
) -> CartaoRead:
    return await CartaoService.create(db, cartao_in)


@router.get("/{cartao_id}", response_model=CartaoRead)
async def get_cartao(cartao_id: int, db: AsyncSession = Depends(get_db)) -> CartaoRead:
    cartao = await CartaoService.get(db, cartao_id)
    if not cartao:
        raise HTTPException(status_code=404, detail="Cartão não encontrado")
    return cartao


@router.get("/", response_model=list[CartaoRead])
async def list_cartoes(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
) -> list[CartaoRead]:
    return await CartaoService.list(db, skip, limit)


@router.put("/{cartao_id}", response_model=CartaoRead)
async def update_cartao(
    cartao_id: int, data: CartaoCreate, db: AsyncSession = Depends(get_db)
) -> CartaoRead:
    updated = await CartaoService.update(db, cartao_id, data.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Cartão não encontrado")
    return updated


@router.delete("/{cartao_id}")
async def delete_cartao(
    cartao_id: int, db: AsyncSession = Depends(get_db)
) -> dict[str, bool]:
    deleted = await CartaoService.delete(db, cartao_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Cartão não encontrado")
    return {"ok": True}
