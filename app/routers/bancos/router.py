from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.usuario import UsuarioCreate, UsuarioRead
from app.services.usuario_service import UsuarioService

router = APIRouter()


@router.post("/", response_model=UsuarioRead)
async def create_usuario(
    usuario_in: UsuarioCreate, db: AsyncSession = Depends(get_db)
) -> UsuarioRead:
    return await UsuarioService.create(db, usuario_in)


@router.get("/{usuario_id}", response_model=UsuarioRead)
async def get_usuario(
    usuario_id: int, db: AsyncSession = Depends(get_db)
) -> UsuarioRead:
    usuario = await UsuarioService.get(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


@router.get("/", response_model=list[UsuarioRead])
async def list_usuarios(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
) -> list[UsuarioRead]:
    return await UsuarioService.list(db, skip, limit)


@router.put("/{usuario_id}", response_model=UsuarioRead)
async def update_usuario(
    usuario_id: int, data: UsuarioCreate, db: AsyncSession = Depends(get_db)
) -> UsuarioRead:
    updated = await UsuarioService.update(db, usuario_id, data.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return updated


@router.delete("/{usuario_id}")
async def delete_usuario(
    usuario_id: int, db: AsyncSession = Depends(get_db)
) -> dict[str, bool]:
    deleted = await UsuarioService.delete(db, usuario_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"ok": True}
