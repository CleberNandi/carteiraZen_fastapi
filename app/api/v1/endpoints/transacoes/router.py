from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.transacao import TransacaoCreate, TransacaoRead
from app.services.transacao_service import TransacaoService

router = APIRouter()


@router.post("/", response_model=TransacaoRead)
async def create_transacao(
    transacao_in: TransacaoCreate, db: AsyncSession = Depends(get_db)
) -> TransacaoRead:
    return await TransacaoService.create(db, transacao_in)


@router.get("/{transacao_id}", response_model=TransacaoRead)
async def get_transacao(
    transacao_id: int, db: AsyncSession = Depends(get_db)
) -> TransacaoRead:
    transacao = await TransacaoService.get(db, transacao_id)
    if not transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    return transacao


@router.get("/", response_model=list[TransacaoRead])
async def list_transacoes(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
) -> list[TransacaoRead]:
    return await TransacaoService.list(db, skip, limit)


@router.put("/{transacao_id}", response_model=TransacaoRead)
async def update_transacao(
    transacao_id: int, data: TransacaoCreate, db: AsyncSession = Depends(get_db)
) -> TransacaoRead:
    updated = await TransacaoService.update(db, transacao_id, data.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    return updated


@router.delete("/{transacao_id}")
async def delete_transacao(
    transacao_id: int, db: AsyncSession = Depends(get_db)
) -> dict[str, bool]:
    deleted = await TransacaoService.delete(db, transacao_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    return {"ok": True}
