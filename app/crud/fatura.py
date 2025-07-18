# app/crud/fatura.py
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app import models
from app.schemas.fatura import FaturaCreate, FaturaUpdate

FaturaCartaoCredito = models.FaturaCartaoCredito
Auditoria = models.Auditoria


def create_fatura(
    db: Session, fatura: FaturaCreate, user_id: int
) -> FaturaCartaoCredito:
    db_fatura = FaturaCartaoCredito(**fatura.model_dump(), user_id=user_id)
    db.add(db_fatura)
    db.commit()
    db.refresh(db_fatura)
    # Auditoria
    from app import models

    auditoria = models.Auditoria(
        tabela="faturas",
        registro_id=db_fatura.id,
        acao="create",
        user_id=user_id,
        dados_depois=str(fatura.model_dump()),
    )
    db.add(auditoria)
    db.commit()
    return db_fatura


def get_fatura(db: Session, fatura_id: int) -> FaturaCartaoCredito | None:
    return (
        db.query(FaturaCartaoCredito)
        .filter(
            FaturaCartaoCredito.id == fatura_id,
            FaturaCartaoCredito.deleted_at.is_(None),
        )
        .first()
    )


def validar_unicidade(
    db: Session,
    cartao_id: int,
    mes: int,
    ano: int,
) -> bool | dict[str, int]:
    fatura = (
        db.query(FaturaCartaoCredito)
        .filter(
            FaturaCartaoCredito.cartao_id == cartao_id,
            FaturaCartaoCredito.mes == mes,
            FaturaCartaoCredito.ano == ano,
            FaturaCartaoCredito.ativo,
        )
        .first()
    )

    if not fatura:
        return True

    return {"id": fatura.id}


def get_faturas(
    db: Session, skip: int = 0, limit: int = 100
) -> list[FaturaCartaoCredito]:
    return (
        db.query(FaturaCartaoCredito)
        .filter(FaturaCartaoCredito.deleted_at.is_(None))
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_fatura(
    db: Session, fatura_id: int, fatura: FaturaUpdate, executor_id: int
) -> FaturaCartaoCredito | None:
    db_fatura = get_fatura(db, fatura_id)
    if not db_fatura:
        return None
    dados_antes = db_fatura.__dict__.copy()
    for attr, value in fatura.model_dump(exclude_unset=True).items():
        setattr(db_fatura, attr, value)
    db_fatura.updated_by = executor_id  # type: ignore[attr-defined]
    db_fatura.updated_at = datetime.now(UTC)  # type: ignore[attr-defined]
    db.commit()
    db.refresh(db_fatura)
    # Auditoria
    auditoria = Auditoria(
        tabela="faturas",
        registro_id=db_fatura.id,
        acao="update",
        user_id=executor_id,
        dados_antes=str(dados_antes),
        dados_depois=str(fatura.model_dump()),
    )
    db.add(auditoria)
    db.commit()
    db.refresh(db_fatura)
    return db_fatura


def delete_fatura(db: Session, fatura_id: int, executor_id: int) -> bool:
    db_fatura = get_fatura(db, fatura_id)
    if not db_fatura:
        return False
    db_fatura.deleted_by = executor_id  # type: ignore[attr-defined]
    db_fatura.deleted_at = datetime.now(UTC)  # type: ignore[attr-defined]
    db.commit()
    db.refresh(db_fatura)
    # Auditoria
    auditoria = Auditoria(
        tabela="faturas",
        registro_id=db_fatura.id,
        acao="delete",
        user_id=executor_id,
        dados_antes=str(db_fatura.__dict__),
    )
    db.add(auditoria)
    db.commit()
    return True
