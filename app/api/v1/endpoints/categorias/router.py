from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.dependencies import get_current_user
from app.models.usuario import Usuario
from app.schemas.categoria import CategoriaCreate, CategoriaRead
from app.services.categoria_service import Categoria, CategoriaService

router = APIRouter()


@router.get("/", response_model=list[CategoriaRead])
async def listar_categorias(
    *,
    incluir_subcategorias: bool = True,
    apenas_principais: bool = False,
    apenas_personalizadas: bool = False,
    db: AsyncSession = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_user),
) -> list[CategoriaRead]:
    return await CategoriaService.listar(
        db,
        current_user,
        incluir_subcategorias,
        apenas_principais,
        apenas_personalizadas,
    )


@router.get("/{categoria_id}", response_model=CategoriaRead)
async def obter_categoria(
    categoria_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_user),
) -> Categoria:
    return await CategoriaService.obter(db, current_user, categoria_id)


@router.get("/{categoria_id}/subcategorias", response_model=list[CategoriaRead])
async def listar_subcategorias(
    categoria_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_user),
) -> list[CategoriaRead]:
    return await CategoriaService.listar_subcategorias(db, current_user, categoria_id)


@router.post("/", response_model=CategoriaRead)
async def criar_categoria_personalizada(
    request: CategoriaCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_user),
) -> Categoria:
    return await CategoriaService.criar(db, current_user, request)


@router.put("/{categoria_id}", response_model=CategoriaRead)
async def atualizar_categoria(
    categoria_id: int,
    request: CategoriaCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_user),
) -> Categoria:
    return await CategoriaService.atualizar(db, current_user, categoria_id, request)
