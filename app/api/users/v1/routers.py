from typing import Any

from core.dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import user as crud_user
from app.crud.user import UserCreationRequiresUserIdError
from app.db.session import get_db
from app.schemas.user import UserCreate, UserOut

router = APIRouter()


@router.get("/", tags=["Root"])
def root() -> dict[str, str]:
    return {"message": "Hello, FastAPI!"}


@router.get("/users/", response_model=list[UserOut], tags=["Users"])
def read_users(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),  # noqa: B008
    _: UserOut = Depends(get_current_user),  # noqa: B008
) -> list[Any]:
    users: list[Any] = crud_user.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=UserOut, tags=["Users"])
def read_user(
    user_id: int,
    _: dict[str, str] = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> UserOut:
    db_user = crud_user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.get("/users/by-email/{email}", response_model=UserOut, tags=["Users"])
def read_user_by_email(
    email: str,
    _: UserOut = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008,
) -> UserOut:
    db_user = crud_user.get_user_by_email(db, email=email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.post("/users/", response_model=UserOut, tags=["Users"])
def create_user(
    user: UserCreate,
    current_user: UserOut = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> UserOut:
    db_user = crud_user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    try:
        return crud_user.create_user(db=db, user=user, user_id=current_user.id)
    except UserCreationRequiresUserIdError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.put("/users/{user_id}", response_model=UserOut, tags=["Users"])
def update_user(
    user_id: int,
    user: UserCreate,
    current_user: UserOut = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> UserOut:
    db_user = crud_user.update_user(
        db=db, user_id=user_id, user=user, executor_id=current_user.id
    )
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.delete("/users/{user_id}", tags=["Users"])
def delete_user(
    user_id: int,
    current_user: UserOut = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> dict[str, str]:
    sucesso = crud_user.delete_user(db=db, user_id=user_id, executor_id=current_user.id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted successfully"}
