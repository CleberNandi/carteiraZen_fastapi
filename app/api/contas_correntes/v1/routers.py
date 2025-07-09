from collections.abc import Sequence

from core.dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.crud.conta_corrente import (
    create_conta_corrente,
    delete_conta_corrente,
    get_conta_corrente,
    get_contas_correntes,
    update_conta_corrente,
)
from app.db.session import get_db
from app.schemas.conta_corrente import ContaCorrente, ContaCorrenteCreate

router = APIRouter(prefix="/contas-correntes", tags=["Contas Correntes"])


@router.get("/", response_model=list[ContaCorrente])
def listar_contas(
    skip: int = 0,
    limit: int = 100,
    current_user: dict[str, str] = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> Sequence[ContaCorrente]:
    return get_contas_correntes(db, skip=skip, limit=limit)


@router.get("/{conta_id}", response_model=ContaCorrente)
def obter_conta(
    conta_id: int,
    current_user: dict[str, str] = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> ContaCorrente | None:
    conta = get_conta_corrente(db, conta_id)
    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    return conta


@router.post("/", response_model=ContaCorrente)
def criar_conta(
    conta: ContaCorrenteCreate,
    user_id: int = Query(...),
    current_user: dict[str, str] = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> ContaCorrente:
    return create_conta_corrente(db, conta, user_id)


@router.put("/{conta_id}", response_model=ContaCorrente)
def atualizar_conta(
    conta_id: int,
    conta: ContaCorrenteCreate,
    executor_id: int = Query(...),
    current_user: dict[str, str] = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> ContaCorrente | None:
    c = update_conta_corrente(db, conta_id, conta, executor_id)
    if not c:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    return c


@router.delete("/{conta_id}")
def deletar_conta(
    conta_id: int,
    executor_id: int = Query(...),
    current_user: dict[str, str] = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> dict[str, bool] | None:
    ok = delete_conta_corrente(db, conta_id, executor_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    return {"ok": True}
