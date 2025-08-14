from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.fatura import FaturaCreate, FaturaRead
from app.services.fatura_service import FaturaService

router = APIRouter()


@router.post("/", response_model=FaturaRead)
async def create_fatura(fatura_in: FaturaCreate, db: AsyncSession = Depends(get_db)):
    return await FaturaService.create(db, fatura_in)


@router.get("/{fatura_id}", response_model=FaturaRead)
async def get_fatura(fatura_id: int, db: AsyncSession = Depends(get_db)):
    fatura = await FaturaService.get(db, fatura_id)
    if not fatura:
        raise HTTPException(status_code=404, detail="Fatura não encontrada")
    return fatura


@router.get("/", response_model=List[FaturaRead])
async def list_faturas(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    return await FaturaService.list(db, skip, limit)


@router.put("/{fatura_id}", response_model=FaturaRead)
async def update_fatura(
    fatura_id: int, data: FaturaCreate, db: AsyncSession = Depends(get_db)
):
    updated = await FaturaService.update(db, fatura_id, data.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Fatura não encontrada")
    return updated


@router.delete("/{fatura_id}")
async def delete_fatura(fatura_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await FaturaService.delete(fatura_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Fatura não encontrada")
    return {"ok": True}
