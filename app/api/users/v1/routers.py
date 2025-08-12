from core.dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import user as crud_user
from app.db.session import get_db
from app.schemas.user import UserCreate, UserOut
from app.services.usuarios import UserCreationRequiresUserIdError, UsuarioService

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
) -> list[UserOut]:
    return UsuarioService(db).listar(skip=skip, limit=limit)


@router.get("/users/{user_id}", response_model=UserOut, tags=["Users"])
def read_user(
    user_id: int,
    _: dict[str, str] = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> UserOut:
    db_user = UsuarioService(db).buscar_por_id(user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.get("/users/by-email/{email}", response_model=UserOut, tags=["Users"])
def read_user_by_email(
    email: str,
    _: UserOut = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008,
) -> UserOut:
    db_user = UsuarioService(db).buscar_por_email(email=email)
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
        return UsuarioService(db).criar(dados=user, executor_id=current_user.id)
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
    return UsuarioService(db).atualizar(
        user_id=user_id, user_data=user, executor_id=current_user.id
    )


@router.delete(
    "/users/{user_id}", tags=["Users"], status_code=status.HTTP_204_NO_CONTENT
)
def delete_user(
    user_id: int,
    current_user: UserOut = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> None:
    sucesso = UsuarioService(db).deletar(user_id=user_id, executor_id=current_user.id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
