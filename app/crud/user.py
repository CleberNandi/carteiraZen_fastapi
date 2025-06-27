from sqlalchemy.orm import Session

from app.models.auditoria import Auditoria
from app.models.user import User as UserModel
from app.schemas.user import UserCreate


# Função para buscar usuário por ID
def get_user(db: Session, user_id: int) -> UserModel | None:
    return db.query(UserModel).filter(UserModel.id == user_id).first()


# Função para buscar usuário por email
def get_user_by_email(db: Session, email: str) -> UserModel | None:
    return db.query(UserModel).filter(UserModel.email == email).first()


# Função para listar usuários com paginação
def get_users(db: Session, skip: int = 0, limit: int = 10) -> list[UserModel]:
    return db.query(UserModel).offset(skip).limit(limit).all()


# Função para criar usuário
def create_user(db: Session, user: UserCreate, user_id: int) -> UserModel:
    db_user = UserModel(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # Auditoria
    auditoria = Auditoria(
        tabela="users",
        registro_id=db_user.id,
        acao="create",
        user_id=user_id,
        dados_depois=str(user.model_dump()),
    )
    db.add(auditoria)
    db.commit()
    return db_user


def update_user(
    db: Session, user_id: int, user: UserCreate, executor_id: int
) -> UserModel | None:
    db_user = get_user(db, user_id)
    if db_user is None:
        return None
    dados_antes = db_user.__dict__.copy()
    for attr, value in user.model_dump().items():
        setattr(db_user, attr, value)
    db.commit()
    db.refresh(db_user)
    # Auditoria
    auditoria = Auditoria(
        tabela="users",
        registro_id=db_user.id,
        acao="update",
        user_id=executor_id,
        dados_antes=str(dados_antes),
        dados_depois=str(user.model_dump()),
    )
    db.add(auditoria)
    db.commit()
    return db_user


def delete_user(db: Session, user_id: int, executor_id: int) -> bool:
    db_user = get_user(db, user_id)
    if db_user is None:
        return False
    dados_antes = db_user.__dict__.copy()
    db.delete(db_user)
    db.commit()
    # Auditoria
    auditoria = Auditoria(
        tabela="users",
        registro_id=user_id,
        acao="delete",
        user_id=executor_id,
        dados_antes=str(dados_antes),
    )
    db.add(auditoria)
    db.commit()
    return True
