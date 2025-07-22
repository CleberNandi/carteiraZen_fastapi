from typing import Any

from core.security import gerar_totp_secret, get_password_hash
from fastapi import HTTPException
import pyotp
from sqlalchemy.orm import Session

from app import models
from app.schemas.user import UserCreate

Auditoria = models.Auditoria
User = models.User


class UserCreationRequiresUserIdError(Exception):
    pass


# Função para buscar usuário por ID
def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


# Função para buscar usuário por email
def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


# Função para listar usuários com paginação
def get_users(db: Session, skip: int = 0, limit: int = 10) -> list[User]:
    return db.query(User).offset(skip).limit(limit).all()


# Função para criar usuário
def create_user(db: Session, user: UserCreate, user_id: int | None = None) -> User:
    # Permite user_id ausente apenas se não houver usuários
    total_users = db.query(User).count()
    if total_users > 0 and user_id is None:
        msg = (
            "user_id é obrigatório para criar novos usuários após o primeiro cadastro."
        )
        raise UserCreationRequiresUserIdError(msg)
    if not user or user.hashed_password is None:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    db_user = User(
        name=user.name,
        email=user.email,
        hashed_password=get_password_hash(user.hashed_password),
        totp_secret=user.totp_secret,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        is_2fa_enabled=user.is_2fa_enabled,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # Auditoria
    auditoria = Auditoria(
        tabela="users",
        registro_id=db_user.id,
        acao="create",
        user_id=user_id if user_id is not None else None,
        dados_depois=str(user.model_dump()),
    )
    db.add(auditoria)
    db.commit()
    return db_user


def update_user(
    db: Session, user_id: int, user: UserCreate, executor_id: int
) -> User | None:
    db_user = get_user(db, user_id)
    if db_user is None:
        return None
    dados_antes = db_user.__dict__.copy()
    for attr, value in user.model_dump().items():
        if value is not None and attr == "hashed_password":
            value = get_password_hash(value)
        if value is not None:
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


def ativar_2fa_para_usuario(user: User, db: Session) -> str:
    if not user.totp_secret:
        user.totp_secret = gerar_totp_secret()
    user.is_2fa_enabled = True
    db.commit()
    db.refresh(user)

    totp_uri: str | Any = pyotp.TOTP(user.totp_secret).provisioning_uri(
        name=user.email, issuer_name="CarteiraZen"
    )

    return totp_uri  # isso pode ser usado para gerar QR Code
