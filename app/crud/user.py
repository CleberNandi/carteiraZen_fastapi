from sqlalchemy.orm import Session

from app import models
from app.schemas.user import UserCreate

User = models.User


def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 10) -> list[User]:
    return (
        db.query(User).filter(User.deleted_at.is_(None)).offset(skip).limit(limit).all()
    )


def create_user(db: Session, user: UserCreate, user_id: int) -> User:
    db_user = User(**user.model_dump(), created_by=user_id)
    db.add(db_user)
    db.flush()
    return db_user


def update_user(db: Session, user: User) -> User:
    db.add(user)
    db.flush()
    return user
