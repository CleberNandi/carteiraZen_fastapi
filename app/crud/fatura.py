# app/crud/fatura.py
from sqlalchemy.orm import Session

from app import models
from app.schemas.fatura import FaturaCreate, FaturaUpdate

FaturaCartaoCredito = models.FaturaCartaoCredito


def create_fatura(db: Session, fatura: FaturaCreate) -> FaturaCartaoCredito:
    db_fatura = FaturaCartaoCredito(**fatura.model_dump())
    db.add(db_fatura)
    db.commit()
    db.refresh(db_fatura)
    return db_fatura


def get_fatura(db: Session, fatura_id: int) -> FaturaCartaoCredito | None:
    return (
        db.query(FaturaCartaoCredito)
        .filter(FaturaCartaoCredito.id == fatura_id)
        .first()
    )


def get_faturas(
    db: Session, skip: int = 0, limit: int = 100
) -> list[FaturaCartaoCredito]:
    return db.query(FaturaCartaoCredito).offset(skip).limit(limit).all()


def update_fatura(
    db: Session, fatura_id: int, fatura: FaturaUpdate
) -> FaturaCartaoCredito | None:
    db_fatura = get_fatura(db, fatura_id)
    if not db_fatura:
        return None
    for attr, value in fatura.model_dump(exclude_unset=True).items():
        setattr(db_fatura, attr, value)
    db.commit()
    db.refresh(db_fatura)
    return db_fatura


def delete_fatura(db: Session, fatura_id: int) -> bool:
    db_fatura = get_fatura(db, fatura_id)
    if not db_fatura:
        return False
    db.delete(db_fatura)
    db.commit()
    return True
