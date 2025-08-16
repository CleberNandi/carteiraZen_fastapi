from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.conta import ContaCreate, ContaRead
from app.services.conta_service import ContaService

router = APIRouter()


@router.post("/", response_model=ContaRead)
async def create_conta(
    conta_in: ContaCreate, db: AsyncSession = Depends(get_db)
) -> ContaRead:
    return await ContaService.create(db, conta_in)


@router.get("/{conta_id}", response_model=ContaRead)
async def get_conta(conta_id: int, db: AsyncSession = Depends(get_db)) -> ContaRead:
    conta = await ContaService.get(db, conta_id)
    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    return conta


@router.get("/", response_model=list[ContaRead])
async def list_contas(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
) -> list[ContaRead]:
    return await ContaService.list(db, skip, limit)


@router.put("/{conta_id}", response_model=ContaRead)
async def update_conta(
    conta_id: int, data: ContaCreate, db: AsyncSession = Depends(get_db)
) -> ContaRead:
    updated = await ContaService.update(db, conta_id, data.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    return updated


@router.delete("/{conta_id}")
async def delete_conta(
    conta_id: int, db: AsyncSession = Depends(get_db)
) -> dict[str, bool]:
    deleted = await ContaService.delete(db, conta_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    return {"ok": True}
