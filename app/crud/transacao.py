# app/crud/transacao.py


from uuid import uuid4

from sqlalchemy.orm import Session

from app.models import Transacao
from app.schemas.transacao import TransacaoCreate, TransacaoUpdate


def create_transacao(db: Session, transacao_in: TransacaoCreate) -> Transacao:
    db_transacao = Transacao(**transacao_in.model_dump(), sync_uuid=str(uuid4()))
    db.add(db_transacao)
    db.commit()
    db.refresh(db_transacao)
    return db_transacao


def listar_transacoes_por_usuario(db: Session, user_id: int) -> list[Transacao]:
    return db.query(Transacao).filter(Transacao.user_id == user_id).all()


def get_transacao_by_id_and_user(
    db: Session, transacao_id: int, user_id: int
) -> Transacao | None:
    return (
        db.query(Transacao)
        .filter(Transacao.id == transacao_id, Transacao.user_id == user_id)
        .first()
    )


def update_transacao_by_user(
    db: Session, transacao_id: int, transacao_in: TransacaoUpdate, user_id: int
) -> Transacao | None:
    transacao = get_transacao_by_id_and_user(db, transacao_id, user_id)
    if not transacao:
        return None

    for field, value in transacao_in.model_dump(exclude_unset=True).items():
        setattr(transacao, field, value)

    db.commit()
    db.refresh(transacao)
    return transacao


def delete_transacao_by_user(db: Session, transacao_id: int, user_id: int) -> bool:
    transacao = get_transacao_by_id_and_user(db, transacao_id, user_id)
    if not transacao:
        return False

    db.delete(transacao)
    db.commit()
    return True
