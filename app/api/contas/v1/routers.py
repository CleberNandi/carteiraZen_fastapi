from collections.abc import Sequence

from core.dependencies import get_current_user
from fastapi import APIRouter, Depends
from schemas.conta import ContaCreate, ContaOut, ContaUpdate
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import User
from app.services.contas import ContaService

router = APIRouter(
    prefix="/contas",
    tags=["Contas"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/", response_model=list[ContaOut])
def listar_contas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),  # noqa: B008
) -> Sequence[ContaOut]:
    return ContaService(db).listar(skip=skip, limit=limit)


@router.get("/{conta_id}", response_model=ContaOut)
def obter_conta(
    conta_id: int,
    db: Session = Depends(get_db),  # noqa: B008
) -> ContaOut | None:
    return ContaService(db).obter(conta_id)


@router.post("/", response_model=ContaOut)
def criar_conta(
    conta: ContaCreate,
    current_user: User = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> ContaOut:
    return ContaService(db).criar(conta, current_user.id)


@router.put("/{conta_id}", response_model=ContaOut)
def atualizar_conta(
    conta_id: int,
    conta: ContaUpdate,
    current_user: User = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> ContaOut | None:
    return ContaService(db).atualizar(
        conta_id=conta_id, conta_data=conta, executor_id=current_user.id
    )


@router.delete("/{conta_id}")
def deletar_conta(
    conta_id: int,
    current_user: User = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> dict[str, bool] | None:
    ContaService(db).deletar(conta_id, current_user.id)
    return {"ok": True}
