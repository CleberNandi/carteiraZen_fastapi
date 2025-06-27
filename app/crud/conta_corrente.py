from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.auditoria import Auditoria
from app.models.conta_corrente import ContaCorrente as ContaCorrenteModel
from app.schemas.conta_corrente import ContaCorrenteCreate


def get_conta_corrente(db: Session, conta_id: int) -> ContaCorrenteModel | None:
    return (
        db.query(ContaCorrenteModel)
        .filter(
            ContaCorrenteModel.id == conta_id, ContaCorrenteModel.deleted_at.is_(None)
        )
        .first()
    )


def get_contas_correntes(
    db: Session, skip: int = 0, limit: int = 100
) -> list[ContaCorrenteModel]:
    return (
        db.query(ContaCorrenteModel)
        .filter(ContaCorrenteModel.deleted_at.is_(None))
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_conta_corrente(
    db: Session, conta: ContaCorrenteCreate, user_id: int
) -> ContaCorrenteModel:
    db_conta = ContaCorrenteModel(**conta.model_dump(), created_by=user_id)
    db.add(db_conta)
    db.commit()
    db.refresh(db_conta)
    auditoria = Auditoria(
        tabela="contas_correntes",
        registro_id=db_conta.id,
        acao="create",
        user_id=user_id,
        dados_depois=str(conta.model_dump()),
    )
    db.add(auditoria)
    db.commit()
    return db_conta


def update_conta_corrente(
    db: Session, conta_id: int, conta: ContaCorrenteCreate, user_id: int
) -> ContaCorrenteModel | None:
    db_conta = get_conta_corrente(db, conta_id)
    if db_conta is None:
        return None
    dados_antes = db_conta.__dict__.copy()
    for attr, value in conta.model_dump().items():
        setattr(db_conta, attr, value)
    db_conta.updated_by = user_id
    db_conta.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(db_conta)
    auditoria = Auditoria(
        tabela="contas_correntes",
        registro_id=db_conta.id,
        acao="update",
        user_id=user_id,
        dados_antes=str(dados_antes),
        dados_depois=str(conta.model_dump()),
    )
    db.add(auditoria)
    db.commit()
    return db_conta


def delete_conta_corrente(db: Session, conta_id: int, user_id: int) -> bool:
    db_conta = get_conta_corrente(db, conta_id)
    if db_conta is None:
        return False
    db_conta.deleted_by = user_id
    db_conta.deleted_at = datetime.now(UTC)
    db.commit()
    auditoria = Auditoria(
        tabela="contas_correntes",
        registro_id=db_conta.id,
        acao="delete",
        user_id=user_id,
        dados_antes=str(db_conta.__dict__),
    )
    db.add(auditoria)
    db.commit()
    return True
