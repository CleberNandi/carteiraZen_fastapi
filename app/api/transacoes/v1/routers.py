# app/api/v1/routes/transacao.py
from core.dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import transacao as crud_transacao
from app.db.session import get_db
from app.schemas.transacao import TransacaoCreate, TransacaoRead, TransacaoUpdate

router = APIRouter(prefix="/transacoes", tags=["Transações"])


@router.post("/", response_model=TransacaoRead, status_code=status.HTTP_201_CREATED)
def create_transacao(
    transacao: TransacaoCreate,
    current_user: dict[str, str] = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
    user_id: int = 1,  # Default user_id for testing, replace with actual user context
) -> TransacaoCreate:
    return crud_transacao.create_transacao(db, transacao, user_id)


@router.get("/", response_model=list[TransacaoRead])
def list_transacoes(
    current_user: dict[str, str] = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> list[TransacaoRead]:
    transacoes = crud_transacao.get_transacoes(db)
    return [TransacaoRead.model_validate(c) for c in transacoes]


@router.get("/{transacao_id}", response_model=TransacaoRead)
def get_transacao(
    transacao_id: int,
    current_user: dict[str, str] = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> TransacaoRead:
    db_transacao = crud_transacao.get_transacao(db, transacao_id)
    if not db_transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    return db_transacao


@router.put("/{transacao_id}", response_model=TransacaoRead)
def update_transacao(
    transacao_id: int,
    transacao: TransacaoUpdate,
    current_user: dict[str, str] = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> TransacaoRead:
    updated = crud_transacao.update_transacao(db, transacao_id, transacao)
    if not updated:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    return updated


@router.delete("/{transacao_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transacao(
    transacao_id: int,
    current_user: dict[str, str] = Depends(get_current_user),  # noqa: B008,
    db: Session = Depends(get_db),  # noqa: B008
) -> None:
    deleted = crud_transacao.delete_transacao(db, transacao_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
