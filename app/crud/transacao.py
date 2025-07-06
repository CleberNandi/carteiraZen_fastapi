# app/crud/transacao.py
from sqlalchemy.orm import Session

from app import models
from app.schemas.transacao import TransacaoCreate, TransacaoUpdate

Transacao = models.Transacao


def create_transacao(db: Session, transacao: TransacaoCreate) -> Transacao:
    db_transacao = Transacao(**transacao.model_dump())
    db.add(db_transacao)
    db.commit()
    db.refresh(db_transacao)
    return db_transacao


def get_transacao(db: Session, transacao_id: int) -> Transacao | None:
    return db.query(Transacao).filter(Transacao.id == transacao_id).first()


def get_transacoes(db: Session, skip: int = 0, limit: int = 100) -> list[Transacao]:
    return db.query(Transacao).offset(skip).limit(limit).all()


def update_transacao(
    db: Session, transacao_id: int, transacao: TransacaoUpdate
) -> Transacao | None:
    db_transacao = get_transacao(db, transacao_id)
    if not db_transacao:
        return None
    for attr, value in transacao.model_dump(exclude_unset=True).items():
        setattr(db_transacao, attr, value)
    db.commit()
    db.refresh(db_transacao)
    return db_transacao


def delete_transacao(db: Session, transacao_id: int) -> bool:
    db_transacao = get_transacao(db, transacao_id)
    if not db_transacao:
        return False
    db.delete(db_transacao)
    db.commit()
    return True
