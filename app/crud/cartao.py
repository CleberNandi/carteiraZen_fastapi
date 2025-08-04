from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app import models
from app.schemas.cartao import CartaoCreate

Auditoria = models.Auditoria
Cartao = models.Cartao


def get_cartao(db: Session, cartao_id: int) -> Cartao | None:
    return (
        db.query(Cartao)
        .filter(Cartao.id == cartao_id, Cartao.deleted_at.is_(None))
        .first()
    )


def get_cartao_by_codigo(db: Session, codigo: str) -> Cartao | None:
    return (
        db.query(Cartao)
        .filter(Cartao.id == codigo, Cartao.deleted_at.is_(None))
        .first()
    )


def get_cartoes(db: Session, skip: int = 0, limit: int = 100) -> list[Cartao]:
    return (
        db.query(Cartao)
        .filter(Cartao.deleted_at.is_(None))
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_cartao(db: Session, cartao: CartaoCreate, user_id: int) -> Cartao:
    db_cartao = Cartao(
        **cartao.model_dump(), created_by=user_id, sync_uuid=str(uuid4())
    )
    db.add(db_cartao)
    db.commit()
    db.refresh(db_cartao)
    # Auditoria
    auditoria = Auditoria(
        tabela="cartoes",
        registro_id=db_cartao.id,
        acao="create",
        user_id=user_id,
        dados_depois=str(cartao.model_dump()),
    )
    db.add(auditoria)
    db.commit()
    return db_cartao


def update_cartao(
    db: Session, cartao_id: int, cartao: CartaoCreate, user_id: int
) -> Cartao | None:
    db_cartao = get_cartao(db, cartao_id)
    if db_cartao is None:
        return None
    dados_antes = db_cartao.__dict__.copy()
    for attr, value in cartao.model_dump().items():
        setattr(db_cartao, attr, value)
    db_cartao.updated_by = user_id  # type: ignore[attr-defined]
    db_cartao.updated_at = datetime.now(UTC)  # type: ignore[attr-defined]
    db.commit()
    db.refresh(db_cartao)
    # Auditoria
    auditoria = Auditoria(
        tabela="cartoes",
        registro_id=db_cartao.id,
        acao="update",
        user_id=user_id,
        dados_antes=str(dados_antes),
        dados_depois=str(cartao.model_dump()),
    )
    db.add(auditoria)
    db.commit()
    return db_cartao


def delete_cartao(db: Session, cartao_id: int, user_id: int) -> bool:
    db_cartao = get_cartao(db, cartao_id)
    if db_cartao is None:
        return False
    db_cartao.deleted_by = user_id  # type: ignore[attr-defined]
    db_cartao.deleted_at = datetime.now(UTC)  # type: ignore[attr-defined]
    db.commit()
    # Auditoria
    auditoria = Auditoria(
        tabela="cartoes",
        registro_id=db_cartao.id,
        acao="delete",
        user_id=user_id,
        dados_antes=str(db_cartao.__dict__),
    )
    db.add(auditoria)
    db.commit()
    return True
