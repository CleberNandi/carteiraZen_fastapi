from collections.abc import Sequence

from core.dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from schemas.user import UserOut
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.banco import Banco, BancoCreate
from app.services.bancos import BancoService

router = APIRouter()


@router.get("/bancos/", response_model=list[Banco], tags=["Bancos"])
def read_bancos(
    skip: int = 0,
    limit: int = 100,
    _: UserOut = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> Sequence[Banco]:
    return BancoService(db).listar(skip=skip, limit=limit)


@router.get("/bancos/{banco_id}", response_model=Banco, tags=["Bancos"])
def read_banco(
    banco_id: int,
    _: UserOut = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> Banco:
    db_banco = BancoService(db).buscar_por_id(banco_id=banco_id)
    if db_banco is None:
        raise HTTPException(status_code=404, detail="Banco não encontrado")
    return db_banco


@router.post("/bancos/", response_model=Banco, tags=["Bancos"])
def create_banco(
    banco: BancoCreate,
    current_user: UserOut = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> Banco:
    return BancoService(db).criar(dados=banco, user_id=current_user.id)


@router.put("/bancos/{banco_id}", response_model=Banco, tags=["Bancos"])
def update_banco(
    banco_id: int,
    banco: BancoCreate,
    current_user: UserOut = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> Banco:
    return BancoService(db).atualizar(
        banco_id=banco_id, dados=banco, user_id=current_user.id
    )


@router.delete("/bancos/{banco_id}", tags=["Bancos"])
def delete_banco(
    banco_id: int,
    current_user: UserOut = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> dict[str, str]:
    BancoService(db).remover(banco_id=banco_id, user_id=current_user.id)
    return {"detail": "Banco removido com sucesso"}
