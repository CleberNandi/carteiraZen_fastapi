from collections.abc import Sequence

from core.dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import User
from app.schemas.agencia import Agencia, AgenciaCreate
from app.services.agencias import AgenciaService

router = APIRouter(
    prefix="/agencias", tags=["Agências"], dependencies=[Depends(get_current_user)]
)


@router.get("/", response_model=list[Agencia])
def listar_agencias(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),  # noqa: B008
) -> Sequence[Agencia]:
    return AgenciaService(db).listar(skip, limit)


@router.get("/{agencia_id}", response_model=Agencia)
def obter_agencia(
    agencia_id: int,
    db: Session = Depends(get_db),  # noqa: B008
) -> Agencia:
    agencia = AgenciaService(db).buscar_por_id(agencia_id)
    if not agencia:
        raise HTTPException(status_code=404, detail="Agência não encontrada")
    return agencia


@router.post("/", response_model=Agencia)
def criar_agencia(
    agencia: AgenciaCreate,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> Agencia:
    return AgenciaService(db).criar(agencia, current_user.id)


@router.put("/{agencia_id}", response_model=Agencia)
def atualizar_agencia(
    agencia_id: int,
    agencia: AgenciaCreate,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> Agencia:
    return AgenciaService(db).atualizar(agencia_id, agencia, current_user.id)


@router.delete("/{agencia_id}")
def deletar_agencia(
    agencia_id: int,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> dict[str, str]:
    AgenciaService(db).remover(agencia_id, current_user.id)
    return {"detail": "Agência removida com sucesso"}
