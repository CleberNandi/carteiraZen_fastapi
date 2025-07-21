from collections.abc import Sequence

from core.dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.agencia import (
    create_agencia,
    delete_agencia,
    get_agencia,
    get_agencias,
    update_agencia,
)
from app.db.session import get_db
from app.models import User
from app.schemas.agencia import Agencia, AgenciaCreate

router = APIRouter(
    prefix="/agencias", tags=["Agências"], dependencies=[Depends(get_current_user)]
)


@router.get("/", response_model=list[Agencia])
def listar_agencias(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),  # noqa: B008
) -> Sequence[Agencia]:
    return get_agencias(db, skip=skip, limit=limit)


@router.get("/{agencia_id}", response_model=Agencia)
def obter_agencia(
    agencia_id: int,
    db: Session = Depends(get_db),  # noqa: B008
) -> Agencia | None:
    agencia = get_agencia(db, agencia_id)
    if not agencia:
        raise HTTPException(status_code=404, detail="Agência não encontrada")
    return agencia


@router.post("/", response_model=Agencia)
def criar_agencia(
    agencia: AgenciaCreate,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> Agencia:
    return create_agencia(db, agencia, current_user.id)


@router.put("/{agencia_id}", response_model=Agencia)
def atualizar_agencia(
    agencia_id: int,
    agencia: AgenciaCreate,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> Agencia | None:
    ag = update_agencia(db, agencia_id, agencia, current_user.id)
    if not ag:
        raise HTTPException(status_code=404, detail="Agência não encontrada")
    return ag


@router.delete("/{agencia_id}")
def deletar_agencia(
    agencia_id: int,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> dict[str, bool]:
    ok = delete_agencia(db, agencia_id, current_user.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Agência não encontrada")
    return {"ok": True}
