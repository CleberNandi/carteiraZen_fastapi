from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models
from app.schemas.conta_corrente import ContaCreate, ContaUpdate
from app.utils.auditoria_utils import registrar_auditoria, serialize_mapped
from app.utils.model_utils import apply_update_fields

Auditoria = models.Auditoria
ContaCorrente = models.ContaCorrente


def get_conta_corrente(db: Session, conta_id: int) -> ContaCorrente | None:
    return (
        db.query(ContaCorrente)
        .filter(ContaCorrente.id == conta_id, ContaCorrente.deleted_at.is_(None))
        .first()
    )


def get_contas_correntes(
    db: Session, skip: int = 0, limit: int = 100
) -> list[ContaCorrente]:
    return (
        db.query(ContaCorrente)
        .filter(ContaCorrente.deleted_at.is_(None))
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_conta_corrente(
    db: Session, conta: ContaCreate, user_id: int
) -> ContaCorrente:
    db_conta = ContaCorrente(**conta.model_dump(), created_by=user_id)
    db.add(db_conta)
    db.flush()

    registrar_auditoria(
        db=db,
        tabela="contas_correntes",
        registro_id=db_conta.id,
        acao="create",
        user_id=user_id,
        dados_depois=conta.model_dump(),
    )

    db.commit()
    db.refresh(db_conta)

    return db_conta


def update_conta_corrente(
    db: Session, conta_id: int, conta_data: ContaUpdate, user_id: int
) -> ContaCorrente | None:
    db_conta = get_conta_corrente(db, conta_id)
    if db_conta is None:
        raise HTTPException(status_code=404, detail="Conta corrente não encontrada")

    dados_antes = serialize_mapped(db_conta)

    campos_alterados = apply_update_fields(
        model=db_conta,
        data=conta_data,
        fields=["nome", "digito", "tipo", "ativo"],
        ignore_none=True,
    )

    if not campos_alterados:
        return db_conta  # Nenhuma mudança, evita auditoria desnecessária

    db_conta.updated_by = user_id
    db_conta.updated_at = datetime.now(UTC)

    registrar_auditoria(
        db=db,
        tabela="contas_correntes",
        registro_id=db_conta.id,
        acao="update",
        user_id=user_id,
        dados_antes=dados_antes,
        dados_input=conta_data.model_dump(),
        dados_depois=serialize_mapped(db_conta),
    )

    db.commit()
    db.refresh(db_conta)

    return db_conta


def delete_conta_corrente(db: Session, conta_id: int, user_id: int) -> bool:
    db_conta = get_conta_corrente(db, conta_id)
    if not db_conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada.")

    dados_antes = serialize_mapped(db_conta)

    db_conta.deleted_by = user_id
    db_conta.deleted_at = datetime.now(UTC)

    registrar_auditoria(
        db=db,
        tabela="contas_correntes",
        registro_id=db_conta.id,
        acao="delete",
        user_id=user_id,
        dados_antes=dados_antes,
    )

    db.commit()
    db.refresh(db_conta)
    return True


def get_conta_corrente_por_numero(
    db: Session, agencia_id: int, numero: str
) -> ContaCorrente | None:
    return (
        db.query(ContaCorrente)
        .filter(
            ContaCorrente.agencia_id == agencia_id,
            ContaCorrente.numero == numero,
            ContaCorrente.ativo.is_(True),
        )
        .first()
    )
