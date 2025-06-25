from sqlalchemy.orm import Session

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
def create_user(db: Session, user: UserCreate) -> UserModel:
    db_user = UserModel(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
