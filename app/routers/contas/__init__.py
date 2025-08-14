from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.services.banco_service import BancoService
from app.schemas.banco import BancoCreate, BancoRead
from app.core.database import get_db

router = APIRouter()

@router.post("/", response_model=BancoRead)
async def create_banco(banco_in: BancoCreate, db: AsyncSession = Depends(get_db)):
    return await BancoService.create(db, banco_in)

@router.get("/{banco_id}", response_model=BancoRead)
async def get_banco(banco_id: int, db: AsyncSession = Depends(get_db)):
    banco = await BancoService.get(db, banco_id)
    if not banco:
        raise HTTPException(status_code=404, detail="Banco não encontrado")
    return banco

@router.get("/", response_model=List[BancoRead])
async def list_bancos(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await BancoService.list(db, skip, limit)

@router.put("/{banco_id}", response_model=BancoRead)
async def update_banco(banco_id: int, data: BancoCreate, db: AsyncSession = Depends(get_db)):
    updated = await BancoService.update(db, banco_id, data.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Banco não encontrado")
    return updated

@router.delete("/{banco_id}")
async def delete_banco(banco_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await BancoService.delete(db, banco_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Banco não encontrado")
    return {"ok": True}
