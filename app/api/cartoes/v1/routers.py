from collections.abc import Sequence

from core.dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from schemas.user import UserOut
from sqlalchemy.orm import Session

from app.crud.cartao import (
    create_cartao,
    delete_cartao,
    get_cartao,
    get_cartoes,
    update_cartao,
)
from app.db.session import get_db
from app.schemas.cartao import Cartao, CartaoCreate

router = APIRouter(prefix="/cartoes", tags=["Cartões"])


@router.get("/", response_model=list[Cartao])
def listar_cartoes(
    skip: int = 0,
    limit: int = 100,
    _: UserOut = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> Sequence[Cartao]:
    return get_cartoes(db, skip=skip, limit=limit)


@router.get("/{cartao_id}", response_model=Cartao)
def obter_cartao(
    cartao_id: int,
    _: UserOut = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> Cartao | None:
    cartao = get_cartao(db, cartao_id)
    if not cartao:
        raise HTTPException(status_code=404, detail="Cartão não encontrado")
    return cartao


@router.post("/", response_model=Cartao)
def criar_cartao(
    cartao: CartaoCreate,
    current_user: UserOut = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> Cartao:
    return create_cartao(db, cartao, current_user.id)


@router.put("/{cartao_id}", response_model=Cartao)
def atualizar_cartao(
    cartao_id: int,
    agencia: CartaoCreate,
    current_user: UserOut = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> Cartao | None:
    cartao = update_cartao(db, cartao_id, agencia, current_user.id)
    if not cartao:
        raise HTTPException(status_code=404, detail="Cartão não encontrado")
    return cartao


@router.delete("/{cartao_id}")
def deletar_cartao(
    cartao_id: int,
    current_user: UserOut = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> dict[str, bool]:
    ok = delete_cartao(db, cartao_id, current_user.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Cartão não encontrado")
    return {"ok": True}
