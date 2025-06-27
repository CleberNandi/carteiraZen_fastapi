from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.auditoria import Auditoria
from app.models.banco import Banco as BancoModel
from app.schemas.banco import BancoCreate


def get_banco(db: Session, banco_id: int) -> BancoModel | None:
    return (
        db.query(BancoModel)
        .filter(BancoModel.id == banco_id, BancoModel.deleted_at.is_(None))
        .first()
    )


def get_banco_by_codigo(db: Session, codigo: str) -> BancoModel | None:
    return (
        db.query(BancoModel)
        .filter(BancoModel.codigo == codigo, BancoModel.deleted_at.is_(None))
        .first()
    )


def get_bancos(db: Session, skip: int = 0, limit: int = 100) -> list[BancoModel]:
    return (
        db.query(BancoModel)
        .filter(BancoModel.deleted_at.is_(None))
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_banco(db: Session, banco: BancoCreate, user_id: int) -> BancoModel:
    db_banco = BancoModel(**banco.model_dump(), created_by=user_id)
    db.add(db_banco)
    db.commit()
    db.refresh(db_banco)
    # Auditoria
    auditoria = Auditoria(
        tabela="bancos",
        registro_id=db_banco.id,
        acao="create",
        user_id=user_id,
        dados_depois=str(banco.model_dump()),
    )
    db.add(auditoria)
    db.commit()
    return db_banco


def update_banco(
    db: Session, banco_id: int, banco: BancoCreate, user_id: int
) -> BancoModel | None:
    db_banco = get_banco(db, banco_id)
    if db_banco is None:
        return None
    dados_antes = db_banco.__dict__.copy()
    for attr, value in banco.model_dump().items():
        setattr(db_banco, attr, value)
    db_banco.updated_by = user_id  # type: ignore[attr-defined]
    db_banco.updated_at = datetime.now(UTC)  # type: ignore[attr-defined]
    db.commit()
    db.refresh(db_banco)
    # Auditoria
    auditoria = Auditoria(
        tabela="bancos",
        registro_id=db_banco.id,
        acao="update",
        user_id=user_id,
        dados_antes=str(dados_antes),
        dados_depois=str(banco.model_dump()),
    )
    db.add(auditoria)
    db.commit()
    return db_banco


def delete_banco(db: Session, banco_id: int, user_id: int) -> bool:
    db_banco = get_banco(db, banco_id)
    if db_banco is None:
        return False
    db_banco.deleted_by = user_id  # type: ignore[attr-defined]
    db_banco.deleted_at = datetime.now(UTC)  # type: ignore[attr-defined]
    db.commit()
    # Auditoria
    auditoria = Auditoria(
        tabela="bancos",
        registro_id=db_banco.id,
        acao="delete",
        user_id=user_id,
        dados_antes=str(db_banco.__dict__),
    )
    db.add(auditoria)
    db.commit()
    return True
