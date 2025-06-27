from collections.abc import Generator
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import user as crud_user
from app.db.session import SessionLocal
from app.schemas.user import User, UserCreate

router = APIRouter()


def get_db() -> Generator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", tags=["Root"])
def root() -> dict[str, str]:
    return {"message": "Hello, FastAPI!"}


@router.get("/users/", response_model=list[User], tags=["Users"])
def read_users(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),  # noqa: B008
) -> list[Any]:
    return crud_user.get_users(db, skip=skip, limit=limit)


@router.get("/users/{user_id}", response_model=User, tags=["Users"])
def read_user(user_id: int, db: Session = Depends(get_db)) -> User:  # noqa: B008
    db_user = crud_user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.get("/users/by-email/{email}", response_model=User, tags=["Users"])
def read_user_by_email(email: str, db: Session = Depends(get_db)) -> User:  # noqa: B008
    db_user = crud_user.get_user_by_email(db, email=email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.post("/users/", response_model=User, tags=["Users"])
def create_user(user: UserCreate, db: Session = Depends(get_db)) -> User:  # noqa: B008
    db_user = crud_user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud_user.create_user(db=db, user=user)
