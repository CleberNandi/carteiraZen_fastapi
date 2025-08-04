# app/crud/categoria.py
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app import models
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate

Categoria = models.Categoria
Auditoria = models.Auditoria


def create_categoria(
    db: Session, categoria: CategoriaCreate, user_id: int
) -> Categoria:
    db_categoria = Categoria(**categoria.model_dump(), sync_uuid=str(uuid4()))
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)

    auditoria = Auditoria(
        tabela="categorias",
        registro_id=db_categoria.id,
        acao="create",
        user_id=user_id,
        dados_depois=str(categoria.model_dump()),
    )
    db.add(auditoria)
    db.commit()
    return db_categoria


def get_categoria(db: Session, categoria_id: int) -> Categoria | None:
    return (
        db.query(Categoria)
        .filter(Categoria.id == categoria_id, Categoria.ativo)
        .first()
    )


def get_categorias(db: Session, skip: int = 0, limit: int = 100) -> list[Categoria]:
    return (
        db.query(Categoria)
        .filter(Categoria.ativo, Categoria.deleted_at.is_(None))
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_categoria(
    db: Session, categoria_id: int, categoria: CategoriaUpdate, user_id: int
) -> Categoria | None:
    db_categoria = get_categoria(db, categoria_id)
    if not db_categoria:
        return None
    dados_antes = db_categoria.__dict__.copy()
    for attr, value in categoria.model_dump(exclude_unset=True).items():
        setattr(db_categoria, attr, value)
    db_categoria.updated_by = user_id  # type: ignore[attr-defined]
    db_categoria.updated_at = datetime.now(UTC)  # type: ignore[attr-defined]
    db.commit()
    db.refresh(db_categoria)

    # Auditoria
    auditoria = Auditoria(
        tabela="categorias",
        registro_id=db_categoria.id,
        acao="update",
        user_id=user_id,
        dados_antes=str(dados_antes),
        dados_depois=str(categoria.model_dump()),
    )
    db.add(auditoria)
    db.commit()
    db.refresh(auditoria)
    return db_categoria


def delete_categoria(db: Session, categoria_id: int, executor_id: int) -> bool:
    db_categoria = get_categoria(db, categoria_id)
    if not db_categoria:
        return False
    db_categoria.ativo = False
    db_categoria.deleted_by = executor_id  # type: ignore[attr-defined]
    db_categoria.deleted_at = datetime.now(UTC)  # type: ignore[attr-defined]
    db.commit()

    # Auditoria
    auditoria = Auditoria(
        tabela="categorias",
        registro_id=db_categoria.id,
        acao="delete",
        user_id=executor_id,
        dados_antes=str(db_categoria.__dict__),
    )
    db.add(auditoria)
    db.commit()
    return True
