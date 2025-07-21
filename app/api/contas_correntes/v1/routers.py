from collections.abc import Sequence

from core.dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.conta_corrente import (
    delete_conta_corrente,
    get_conta_corrente,
    get_contas_correntes,
)
from app.db.session import get_db
from app.models import User
from app.schemas.conta_corrente import ContaCreate, ContaOut, ContaUpdate
from app.services.contas import ContaService

router = APIRouter(
    prefix="/contas-correntes",
    tags=["Contas Correntes"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/", response_model=list[ContaOut])
def listar_contas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),  # noqa: B008
) -> Sequence[ContaOut]:
    return get_contas_correntes(db, skip=skip, limit=limit)


@router.get("/{conta_id}", response_model=ContaOut)
def obter_conta(
    conta_id: int,
    db: Session = Depends(get_db),  # noqa: B008
) -> ContaOut | None:
    conta = get_conta_corrente(db, conta_id)
    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    return conta


@router.post("/", response_model=ContaOut)
def criar_conta(
    conta: ContaCreate,
    current_user: User = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> ContaOut:
    service = ContaService(db)
    return service.criar(conta, current_user.id)


@router.put("/{conta_id}", response_model=ContaOut)
def atualizar_conta(
    conta_id: int,
    conta: ContaUpdate,
    current_user: User = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> ContaOut | None:
    service = ContaService(db)
    c = service.atualizar(
        conta_id=conta_id, conta_data=conta, executor_id=current_user.id
    )

    if not c:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    return c


@router.delete("/{conta_id}")
def deletar_conta(
    conta_id: int,
    current_user: User = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> dict[str, bool] | None:
    ok = delete_conta_corrente(db, conta_id, current_user.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    return {"ok": True}
