from datetime import UTC, datetime
from uuid import uuid4

from schemas.conta import ContaCreate, ContaUpdate
from sqlalchemy.orm import Session

from app import models
from app.utils.auditoria_utils import registrar_auditoria, serialize_mapped
from app.utils.model_utils import apply_update_fields

Auditoria = models.Auditoria
ContaCorrente = models.Conta


def get_conta(db: Session, conta_id: int) -> ContaCorrente | None:
    return (
        db.query(ContaCorrente)
        .filter(ContaCorrente.id == conta_id, ContaCorrente.deleted_at.is_(None))
        .first()
    )


def get_contas(db: Session, skip: int = 0, limit: int = 100) -> list[ContaCorrente]:
    return (
        db.query(ContaCorrente)
        .filter(ContaCorrente.deleted_at.is_(None))
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_conta(db: Session, conta: ContaCreate, user_id: int) -> ContaCorrente:
    db_conta = ContaCorrente(
        **conta.model_dump(), created_by=user_id, sync_uuid=str(uuid4())
    )
    db.add(db_conta)
    db.flush()

    registrar_auditoria(
        db=db,
        tabela="contas",
        registro_id=db_conta.id,
        acao="create",
        user_id=user_id,
        dados_depois=conta.model_dump(),
    )

    db.commit()
    db.refresh(db_conta)

    return db_conta


def update_conta(
    db: Session, conta: ContaCorrente, conta_data: ContaUpdate, user_id: int
) -> ContaCorrente | None:
    dados_antes = serialize_mapped(conta)

    campos_alterados = apply_update_fields(
        model=conta,
        data=conta_data,
        fields=["nome", "tipo", "ativo", "saldo_inicial", "nome"],
    )

    if not campos_alterados:
        return conta  # Nenhuma mudança, evita auditoria desnecessária

    conta.updated_by = user_id
    conta.updated_at = datetime.now(UTC)

    registrar_auditoria(
        db=db,
        tabela="contas",
        registro_id=conta.id,
        acao="update",
        user_id=user_id,
        dados_antes=dados_antes,
        dados_input=conta_data.model_dump(),
        dados_depois=serialize_mapped(conta),
    )

    db.commit()
    db.refresh(conta)

    return conta


def delete_conta(db: Session, conta: ContaCorrente, user_id: int) -> bool:
    dados_antes = serialize_mapped(conta)

    conta.deleted_by = user_id
    conta.deleted_at = datetime.now(UTC)

    registrar_auditoria(
        db=db,
        tabela="contas",
        registro_id=conta.id,
        acao="delete",
        user_id=user_id,
        dados_antes=dados_antes,
    )

    db.commit()
    db.refresh(conta)
    return True


def get_conta_por_numero(db: Session, numero: str) -> ContaCorrente | None:
    return (
        db.query(ContaCorrente)
        .filter(
            ContaCorrente.numero == numero,
            ContaCorrente.ativo.is_(True),
        )
        .first()
    )
