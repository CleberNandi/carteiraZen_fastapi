# app/api/v1/routes/transacao.py

from core.dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.transacao import TransacaoCreate, TransacaoRead, TransacaoUpdate
from app.schemas.user import UserOut
from app.services.transacoes import TransacaoService

router = APIRouter(
    prefix="/transacoes", tags=["Transações"], dependencies=[Depends(get_current_user)]
)


@router.post("/", response_model=TransacaoRead, status_code=status.HTTP_201_CREATED)
def create_transacao(
    transacao: TransacaoCreate,
    current_user: UserOut = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> TransacaoRead:
    service = TransacaoService(db=db, user_id=current_user.id)
    return service.criar(transacao)


@router.get("/", response_model=list[TransacaoRead])
def list_transacoes(
    current_user: UserOut = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> list[TransacaoRead]:
    service = TransacaoService(db=db, user_id=current_user.id)
    return service.listar()


@router.get("/{transacao_id}", response_model=TransacaoRead)
def get_transacao(
    transacao_id: int,
    current_user: UserOut = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> TransacaoRead:
    service = TransacaoService(db=db, user_id=current_user.id)
    transacao = service.buscar_por_id(transacao_id)
    if not transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    return transacao


@router.put("/{transacao_id}", response_model=TransacaoRead)
def update_transacao(
    transacao_id: int,
    transacao: TransacaoUpdate,
    current_user: UserOut = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> TransacaoRead:
    service = TransacaoService(db=db, user_id=current_user.id)
    atualizada = service.atualizar(transacao_id, transacao)
    if not atualizada:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    return atualizada


@router.delete("/{transacao_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transacao(
    transacao_id: int,
    current_user: UserOut = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> None:
    service = TransacaoService(db=db, user_id=current_user.id)
    sucesso = service.remover(transacao_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
