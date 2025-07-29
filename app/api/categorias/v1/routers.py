from core.dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from schemas.user import UserOut
from sqlalchemy.orm import Session

from app.crud.categoria import (
    create_categoria,
    delete_categoria,
    get_categoria,
    get_categorias,
    update_categoria,
)
from app.db.session import get_db
from app.schemas.categoria import CategoriaCreate, CategoriaRead, CategoriaUpdate

router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.post("/", response_model=CategoriaRead)
def create(
    categoria: CategoriaCreate,
    current_user: UserOut = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> CategoriaRead:
    return create_categoria(db, categoria, current_user.id)


@router.get("/", response_model=list[CategoriaRead])
def read_all(
    skip: int = 0,
    limit: int = 100,
    _: UserOut = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> list[CategoriaRead]:
    categorias = get_categorias(db, skip=skip, limit=limit)
    return [CategoriaRead.model_validate(c) for c in categorias]


@router.get("/{categoria_id}", response_model=CategoriaRead)
def read(
    categoria_id: int,
    _: UserOut = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> CategoriaRead:
    categoria = get_categoria(db, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return categoria


@router.put("/{categoria_id}", response_model=CategoriaRead)
def update(
    categoria_id: int,
    categoria: CategoriaUpdate,
    current_user: UserOut = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> CategoriaRead:
    updated = update_categoria(db, categoria_id, categoria, current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return updated


@router.delete("/{categoria_id}", status_code=204)
def delete(
    categoria_id: int,
    current_user: UserOut = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> None:
    if not delete_categoria(db, categoria_id, executor_id=current_user.id):
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
