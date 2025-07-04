from typing import Any

import pyotp
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User


def user_data() -> dict[str, Any]:
    return {
        "name": "Primeiro",
        "email": "primeiro@example.com",
        "hashed_password": "hash123",
        "totp_secret": None,
        "is_active": True,
        "is_superuser": True,
        "is_2fa_enabled": False,
    }


def user_data_2() -> dict[str, Any]:
    return {
        "name": "Segundo",
        "email": "segundo@example.com",
        "hashed_password": "hash123",
        "totp_secret": None,
        "is_active": True,
        "is_superuser": True,
        "is_2fa_enabled": False,
    }


def create_user_without_2fa(get_db: Session):
    user = User(
        name="Usuário Sem 2FA",
        email="sem2fa@example.com",
        hashed_password=get_password_hash("senha123"),
        is_2fa_enabled=False,
        totp_secret=None,
    )
    get_db.add(user)
    get_db.commit()
    get_db.refresh(user)
    return user


def create_user_with_2fa(get_db: Session):
    secret = pyotp.random_base32()
    user = User(
        name="Usuário Com 2FA",
        email="com2fa@example.com",
        hashed_password=get_password_hash("senha123"),
        is_2fa_enabled=True,
        totp_secret=secret,
    )
    get_db.add(user)
    get_db.commit()
    get_db.refresh(user)
    return user
