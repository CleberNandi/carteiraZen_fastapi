from typing import Literal

from core.dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud import fatura as crud_fatura
from app.db.session import get_db
from app.schemas.fatura import FaturaCreate, FaturaRead, FaturaUpdate
from app.schemas.user import UserOut
from app.services.faturas import criar_fatura

router = APIRouter(tags=["Faturas"])


@router.get("/faturas", response_model=list[FaturaRead])
def list_faturas(
    current_user: dict[str, str] = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> list[FaturaRead]:
    faturas = crud_fatura.get_faturas(db)
    return [FaturaRead.model_validate(c) for c in faturas]


# Validação de unicidade
@router.get("/faturas/validar-unicidade")
def validar_unicidade(
    cartao_id: int = Query(..., description="ID do cartão"),
    mes: int = Query(..., description="Mês da fatura"),
    ano: int = Query(..., description="Ano da fatura"),
    current_user: dict[str, str] = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> dict[str, int] | Literal[True]:
    fatura_unica = crud_fatura.validar_unicidade(
        db=db, cartao_id=cartao_id, mes=mes, ano=ano
    )
    if not fatura_unica:
        raise HTTPException(status_code=400, detail="Fatura já existe")
    return fatura_unica


@router.get("/faturas/{fatura_id}", response_model=FaturaRead)
def get_fatura(
    fatura_id: int,
    current_user: dict[str, str] = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> FaturaRead:
    db_fatura = crud_fatura.get_fatura(db, fatura_id)
    if not db_fatura:
        raise HTTPException(status_code=404, detail="Fatura não encontrada")
    return db_fatura


@router.post("/faturas", response_model=FaturaRead, status_code=status.HTTP_201_CREATED)
def create_fatura(
    fatura: FaturaCreate,
    executor_id: int,
    current_user: UserOut = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> FaturaRead:
    return criar_fatura(db, fatura, executor_id)


@router.put("/faturas/{fatura_id}", response_model=FaturaRead)
def update_fatura(
    fatura_id: int,
    fatura: FaturaUpdate,
    executor_id: int,
    current_user: dict[str, str] = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> FaturaRead:
    updated = crud_fatura.update_fatura(db, fatura_id, fatura, executor_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Fatura não encontrada")
    return updated


@router.delete("/faturas/{fatura_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fatura(
    fatura_id: int,
    executor_id: int,
    current_user: dict[str, str] = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> None:
    deleted = crud_fatura.delete_fatura(db, fatura_id, executor_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Fatura não encontrada")
