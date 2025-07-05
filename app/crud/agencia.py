from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.agencia import Agencia as AgenciaModels
from app.models.auditoria import Auditoria
from app.schemas.agencia import AgenciaCreate


def get_agencia(db: Session, agencia_id: int) -> AgenciaModels | None:
    return (
        db.query(AgenciaModels)
        .filter(AgenciaModels.id == agencia_id, AgenciaModels.deleted_at.is_(None))
        .first()
    )


def get_agencias(db: Session, skip: int = 0, limit: int = 100) -> list[AgenciaModels]:
    return (
        db.query(AgenciaModels)
        .filter(AgenciaModels.deleted_at.is_(None))
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_agencia(db: Session, agencia: AgenciaCreate, user_id: int) -> AgenciaModels:
    db_agencia = AgenciaModels(**agencia.model_dump(), created_by=user_id)
    db.add(db_agencia)
    db.commit()
    db.refresh(db_agencia)
    auditoria = Auditoria(
        tabela="agencias",
        registro_id=db_agencia.id,
        acao="create",
        user_id=user_id,
        dados_depois=str(agencia.model_dump()),
    )
    db.add(auditoria)
    db.commit()
    return db_agencia


def update_agencia(
    db: Session, agencia_id: int, agencia: AgenciaCreate, user_id: int
) -> AgenciaModels | None:
    db_agencia = get_agencia(db, agencia_id)
    if db_agencia is None:
        return None
    dados_antes = db_agencia.__dict__.copy()
    for attr, value in agencia.model_dump().items():
        setattr(db_agencia, attr, value)
    db_agencia.updated_by = user_id
    db_agencia.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(db_agencia)
    auditoria = Auditoria(
        tabela="agencias",
        registro_id=db_agencia.id,
        acao="update",
        user_id=user_id,
        dados_antes=str(dados_antes),
        dados_depois=str(agencia.model_dump()),
    )
    db.add(auditoria)
    db.flush()
    db.commit()
    db.refresh(auditoria)
    return db_agencia


def delete_agencia(db: Session, agencia_id: int, user_id: int) -> bool:
    db_agencia = get_agencia(db, agencia_id)
    if db_agencia is None:
        return False
    db_agencia.deleted_by = user_id
    db_agencia.deleted_at = datetime.now(UTC)
    db.commit()
    auditoria = Auditoria(
        tabela="agencias",
        registro_id=db_agencia.id,
        acao="delete",
        user_id=user_id,
        dados_antes=str(db_agencia.__dict__),
    )
    db.add(auditoria)
    db.commit()
    return True
