from typing import Literal

from core.dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.fatura import FaturaCreate, FaturaRead, FaturaUpdate
from app.schemas.user import UserOut
from app.services.faturas import FaturaService

router = APIRouter(
    prefix="/faturas", tags=["Faturas"], dependencies=[Depends(get_current_user)]
)


@router.get("/", response_model=list[FaturaRead])
def list_faturas(
    db: Session = Depends(get_db),  # noqa: B008,
) -> list[FaturaRead]:
    return FaturaService(db).listar()


@router.get("/validar-unicidade")
def validar_unicidade(
    cartao_id: int = Query(..., description="ID do cartão"),
    mes: int = Query(..., description="Mês da fatura"),
    ano: int = Query(..., description="Ano da fatura"),
    db: Session = Depends(get_db),  # noqa: B008,
) -> dict[str, int] | Literal[True]:
    if not FaturaService(db).validar_unicidade(cartao_id, mes, ano):
        raise HTTPException(status_code=400, detail="Fatura já existe")
    return True


@router.get("/{fatura_id}", response_model=FaturaRead)
def get_fatura(
    fatura_id: int,
    db: Session = Depends(get_db),  # noqa: B008,
) -> FaturaRead:
    fatura = FaturaService(db).buscar_por_id(fatura_id)
    if not fatura:
        raise HTTPException(status_code=404, detail="Fatura não encontrada")
    return fatura


@router.post("/", response_model=FaturaRead, status_code=status.HTTP_201_CREATED)
def create_fatura(
    fatura: FaturaCreate,
    current_user: UserOut = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008,
) -> FaturaRead:
    return FaturaService(db).criar(fatura, current_user.id)


@router.put("/{fatura_id}", response_model=FaturaRead)
def update_fatura(
    fatura_id: int,
    fatura: FaturaUpdate,
    current_user: UserOut = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008,
) -> FaturaRead:
    updated = FaturaService(db).atualizar(fatura_id, fatura, current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Fatura não encontrada")
    return updated


@router.delete("/{fatura_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fatura(
    fatura_id: int,
    current_user: UserOut = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008,
) -> None:
    deletado = FaturaService(db).remover(fatura_id, current_user.id)
    if not deletado:
        raise HTTPException(status_code=404, detail="Fatura não encontrada")
