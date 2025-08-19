from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.schemas.transacao_parcela import TransacaoParcelaCreate, TransacaoParcelaRead
from app.services.transacao_parcela_service import TransacaoParcelaService

router = APIRouter()


@router.post("/", response_model=TransacaoParcelaRead)
async def create_parcela(
    parcela_in: TransacaoParcelaCreate,
    db: AsyncSession = Depends(get_async_db),
) -> TransacaoParcelaRead:
    return await TransacaoParcelaService.create(db, parcela_in)


@router.get("/{parcela_id}", response_model=TransacaoParcelaRead)
async def get_parcela(
    parcela_id: int,
    db: AsyncSession = Depends(get_async_db),
) -> TransacaoParcelaRead:
    parcela = await TransacaoParcelaService.get(db, parcela_id)
    if not parcela:
        raise HTTPException(status_code=404, detail="Parcela não encontrada")
    return parcela


@router.get("/", response_model=list[TransacaoParcelaRead])
async def list_parcelas(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db),
) -> list[TransacaoParcelaRead]:
    return await TransacaoParcelaService.list(db, skip, limit)


@router.put("/{parcela_id}", response_model=TransacaoParcelaRead)
async def update_parcela(
    parcela_id: int,
    data: TransacaoParcelaCreate,
    db: AsyncSession = Depends(get_async_db),
) -> TransacaoParcelaRead:
    updated = await TransacaoParcelaService.update(db, parcela_id, data.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Parcela não encontrada")
    return updated


@router.delete("/{parcela_id}")
async def delete_parcela(
    parcela_id: int,
    db: AsyncSession = Depends(get_async_db),
) -> dict[str, bool]:
    deleted = await TransacaoParcelaService.delete(db, parcela_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Parcela não encontrada")
    return {"ok": True}
