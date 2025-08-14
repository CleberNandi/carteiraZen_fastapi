from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.categoria import CategoriaCreate, CategoriaRead
from app.services.categoria_service import CategoriaService

router = APIRouter()


@router.post("/", response_model=CategoriaRead)
async def create_categoria(
    categoria_in: CategoriaCreate, db: AsyncSession = Depends(get_db)
):
    return await CategoriaService.create(db, categoria_in)


@router.get("/{categoria_id}", response_model=CategoriaRead)
async def get_categoria(categoria_id: int, db: AsyncSession = Depends(get_db)):
    categoria = await CategoriaService.get(db, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return categoria


@router.get("/", response_model=List[CategoriaRead])
async def list_categorias(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    return await CategoriaService.list(db, skip, limit)


@router.put("/{categoria_id}", response_model=CategoriaRead)
async def update_categoria(
    categoria_id: int, data: CategoriaCreate, db: AsyncSession = Depends(get_db)
):
    updated = await CategoriaService.update(db, categoria_id, data.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return updated


@router.delete("/{categoria_id}")
async def delete_categoria(categoria_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await CategoriaService.delete(db, categoria_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return {"ok": True}
