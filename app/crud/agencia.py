from sqlalchemy.orm import Session

from app import models
from app.schemas.agencia import AgenciaCreate

Agencia = models.Agencia


def get_agencia(db: Session, agencia_id: int) -> Agencia | None:
    return (
        db.query(Agencia)
        .filter(Agencia.id == agencia_id, Agencia.deleted_at.is_(None))
        .first()
    )


def get_agencias(db: Session, skip: int = 0, limit: int = 100) -> list[Agencia]:
    return (
        db.query(Agencia)
        .filter(Agencia.deleted_at.is_(None))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_agencia_por_numero_banco(
    db: Session, numero: str, banco_id: int
) -> Agencia | None:
    return (
        db.query(Agencia)
        .filter_by(numero=numero, banco_id=banco_id, deleted_at=None)
        .first()
    )


def create_agencia(db: Session, dados: AgenciaCreate, user_id: int) -> Agencia:
    agencia = Agencia(**dados.model_dump(), created_by=user_id)
    db.add(agencia)
    db.flush()
    return agencia


def soft_delete_agencia(db: Session, agencia: Agencia) -> Agencia:
    db.flush()
    return agencia
