from sqlalchemy.orm import Session

from app.models.banco import Banco as BancoModel
from app.schemas.banco import BancoCreate


def get_banco(db: Session, banco_id: int) -> BancoModel | None:
    return db.query(BancoModel).filter(BancoModel.id == banco_id).first()


def get_banco_by_codigo(db: Session, codigo: str) -> BancoModel | None:
    return db.query(BancoModel).filter(BancoModel.codigo == codigo).first()


def get_bancos(db: Session, skip: int = 0, limit: int = 100) -> list[BancoModel]:
    return db.query(BancoModel).offset(skip).limit(limit).all()


def create_banco(db: Session, banco: BancoCreate) -> BancoModel:
    db_banco = BancoModel(**banco.model_dump())
    db.add(db_banco)
    db.commit()
    db.refresh(db_banco)
    return db_banco
