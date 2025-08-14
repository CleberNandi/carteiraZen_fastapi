from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.sub_categoria import SubCategoriaCreate, SubCategoriaRead
from app.services.sub_categoria_service import SubCategoriaService

router = APIRouter()


@router.post("/", response_model=SubCategoriaRead)
async def create_sub_categoria(
    sub_in: SubCategoriaCreate, db: AsyncSession = Depends(get_db)
):
    return await SubCategoriaService.create(db, sub_in)


@router.get("/{sub_id}", response_model=SubCategoriaRead)
async def get_sub_categoria(sub_id: int, db: AsyncSession = Depends(get_db)):
    sub = await SubCategoriaService.get(db, sub_id)
    if not sub:
        raise HTTPException(status_code=404, detail="SubCategoria não encontrada")
    return sub


@router.get("/", response_model=List[SubCategoriaRead])
async def list_sub_categorias(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    return await SubCategoriaService.list(db, skip, limit)


@router.put("/{sub_id}", response_model=SubCategoriaRead)
async def update_sub_categoria(
    sub_id: int, data: SubCategoriaCreate, db: AsyncSession = Depends(get_db)
):
    updated = await SubCategoriaService.update(db, sub_id, data.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="SubCategoria não encontrada")
    return updated


@router.delete("/{sub_id}")
async def delete_sub_categoria(sub_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await SubCategoriaService.delete(db, sub_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="SubCategoria não encontrada")
    return {"ok": True}
