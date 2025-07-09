from collections.abc import Sequence

from core.dependencies import get_current_user
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.crud import auditoria as crud_auditoria
from app.db.session import get_db
from app.schemas.auditoria import Auditoria

router = APIRouter()


@router.get("/auditoria/", response_model=list[Auditoria], tags=["Auditoria"])
def read_auditoria(
    tabela: str | None = Query(None),
    registro_id: int | None = Query(None),
    acao: str | None = Query(None),
    user_id: int | None = Query(None),
    skip: int = 0,
    limit: int = 100,
    current_user: dict[str, str] = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> Sequence[Auditoria]:
    return crud_auditoria.get_auditorias(
        db,
        tabela=tabela,
        registro_id=registro_id,
        acao=acao,
        user_id=user_id,
        skip=skip,
        limit=limit,
    )
