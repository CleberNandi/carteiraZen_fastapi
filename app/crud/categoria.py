# app/crud/categoria.py
from sqlalchemy.orm import Session

from app.models.categoria import Categoria
from app.schemas.categoria import CategoriaCreate, CategoriaRead, CategoriaUpdate


def create_categoria(
    db: Session, categoria: CategoriaCreate, user_id: int
) -> CategoriaRead:
    db_categoria = Categoria(**categoria.model_dump())
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    return db_categoria


def get_categoria(db: Session, categoria_id: int) -> Categoria | None:
    return db.query(Categoria).filter(Categoria.id == categoria_id).first()


def get_categorias(db: Session, skip: int = 0, limit: int = 100) -> list[Categoria]:
    return db.query(Categoria).offset(skip).limit(limit).all()


def update_categoria(
    db: Session, categoria_id: int, categoria: CategoriaUpdate, user_id: int
) -> Categoria | None:
    db_categoria = get_categoria(db, categoria_id)
    if not db_categoria:
        return None
    for attr, value in categoria.model_dump(exclude_unset=True).items():
        setattr(db_categoria, attr, value)
    db.commit()
    db.refresh(db_categoria)
    return db_categoria


def delete_categoria(db: Session, categoria_id: int) -> bool:
    db_categoria = get_categoria(db, categoria_id)
    if not db_categoria:
        return False
    db.delete(db_categoria)
    db.commit()
    return True
