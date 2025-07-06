# app/api/v1/routes/fatura.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import fatura as crud_fatura
from app.db.session import get_db
from app.schemas.fatura import FaturaCreate, FaturaRead, FaturaUpdate

router = APIRouter(prefix="/faturas", tags=["Faturas"])


@router.post("/", response_model=FaturaRead, status_code=status.HTTP_201_CREATED)
def create_fatura(
    fatura: FaturaCreate,
    db: Session = Depends(get_db),  # noqa: B008
    user_id: int = 1,  # Default user_id for testing, replace with actual user context
) -> FaturaRead:
    return crud_fatura.create_fatura(db, fatura, user_id)


@router.get("/", response_model=list[FaturaRead])
def list_faturas(db: Session = Depends(get_db)) -> list[FaturaRead]:  # noqa: B008
    faturas = crud_fatura.get_faturas(db)
    return [FaturaRead.model_validate(c) for c in faturas]


@router.get("/{fatura_id}", response_model=FaturaRead)
def get_fatura(
    fatura_id: int,
    db: Session = Depends(get_db),  # noqa: B008
) -> FaturaRead:
    db_fatura = crud_fatura.get_fatura(db, fatura_id)
    if not db_fatura:
        raise HTTPException(status_code=404, detail="Fatura não encontrada")
    return db_fatura


@router.put("/{fatura_id}", response_model=FaturaRead)
def update_fatura(
    fatura_id: int,
    fatura: FaturaUpdate,
    db: Session = Depends(get_db),  # noqa: B008
) -> FaturaRead:
    updated = crud_fatura.update_fatura(db, fatura_id, fatura)
    if not updated:
        raise HTTPException(status_code=404, detail="Fatura não encontrada")
    return updated


@router.delete("/{fatura_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fatura(fatura_id: int, db: Session = Depends(get_db)) -> None:  # noqa: B008
    deleted = crud_fatura.delete_fatura(db, fatura_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Fatura não encontrada")
