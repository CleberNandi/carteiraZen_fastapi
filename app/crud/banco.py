from uuid import uuid4

from sqlalchemy.orm import Session

from app import models
from app.schemas.banco import BancoCreate

Banco = models.Banco


def get_banco(db: Session, banco_id: int) -> Banco | None:
    return (
        db.query(Banco)
        .filter(Banco.codigo == banco_id, Banco.deleted_at.is_(None))
        .first()
    )


def get_banco_por_codigo(db: Session, codigo: str) -> Banco | None:
    return (
        db.query(Banco)
        .filter(Banco.codigo == codigo, Banco.deleted_at.is_(None))
        .first()
    )


def get_banco_por_nome(db: Session, nome: str) -> Banco | None:
    return (
        db.query(Banco).filter(Banco.nome == nome, Banco.deleted_at.is_(None)).first()
    )


def get_banco_por_cnpj(db: Session, cnpj: str) -> Banco | None:
    return (
        db.query(Banco).filter(Banco.cnpj == cnpj, Banco.deleted_at.is_(None)).first()
    )


def get_bancos(db: Session, skip: int = 0, limit: int = 100) -> list[Banco]:
    return (
        db.query(Banco)
        .filter(Banco.deleted_at.is_(None))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_banco_por_cnpj_todos(db: Session, cnpj: str) -> Banco | None:
    return db.query(Banco).filter(Banco.cnpj == cnpj).first()


def get_banco_por_codigo_todos(db: Session, codigo: str) -> Banco | None:
    return db.query(Banco).filter(Banco.codigo == codigo).first()


def get_banco_por_nome_todos(db: Session, nome: str) -> Banco | None:
    return db.query(Banco).filter(Banco.nome == nome).first()


def create_banco(db: Session, banco: BancoCreate, user_id: int | None) -> Banco:
    db_banco = Banco(**banco.model_dump(), created_by=user_id, sync_uuid=str(uuid4()))
    db.add(db_banco)
    db.flush()
    return db_banco


def soft_delete_banco(db: Session, banco: Banco) -> Banco:
    db.flush()
    return banco
