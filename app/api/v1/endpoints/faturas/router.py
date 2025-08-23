from fastapi import APIRouter, Depends, HTTPException, Query, status
from services.fatura_service import FaturaService
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.core.database import get_async_db
from app.core.dependencies import get_current_user
from app.models import fatura, transacao, usuario
from app.schemas.fatura import (
    FaturaPagamentoCreate,
    FaturaPagamentoResponse,
    FaturaResponse,
    FaturasResumoResponse,
    FaturasVencidasAlertaResponse,
)
from app.schemas.transacao import TransacaoResponse

Fatura = fatura.Fatura
Usuario = usuario.Usuario
Transacao = transacao.Transacao

router = APIRouter()


@router.get("/", response_model=list[FaturaResponse])
def listar_faturas(
    db: Session = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    cartao_id: int | None = None,
    ano: int | None = None,
    mes: int | None = None,
    *,
    apenas_pendentes: bool = False,
    apenas_vencidas: bool = False,
) -> list[FaturaResponse]:
    """Lista as faturas do usuário com filtros opcionais"""
    query = db.query(Fatura).filter(Fatura.usuario_id == current_user.id)

    if cartao_id:
        query = query.filter(Fatura.cartao_id == cartao_id)

    if ano:
        query = query.filter(func.extract("year", Fatura.data_vencimento) == ano)

    if mes:
        query = query.filter(func.extract("month", Fatura.data_vencimento) == mes)

    if apenas_pendentes:
        query = query.filter(~Fatura.paga)

    if apenas_vencidas:
        query = query.filter(Fatura.vencida.is_(True), Fatura.paga.is_(False))

    return [
        FaturaResponse.model_validate(f) for f in query.offset(skip).limit(limit).all()
    ]


@router.get("/{fatura_id}", response_model=FaturaResponse)
def obter_fatura(
    fatura_id: int,
    db: Session = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_user),
) -> Fatura:
    """Obtém detalhes de uma fatura específica"""
    fatura = (
        db.query(Fatura)
        .filter(Fatura.id == fatura_id, Fatura.usuario_id == current_user.id)
        .first()
    )

    if not fatura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Fatura não encontrada"
        )

    return fatura


@router.get("/{fatura_id}/transacoes", response_model=list[TransacaoResponse])
def obter_transacoes_fatura(
    fatura_id: int,
    db: Session = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_user),
) -> list[TransacaoResponse]:
    """Obtém as transações de uma fatura"""
    fatura = (
        db.query(Fatura)
        .filter(Fatura.id == fatura_id, Fatura.usuario_id == current_user.id)
        .first()
    )

    if not fatura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Fatura não encontrada"
        )

    return [TransacaoResponse.model_validate(t) for t in fatura.transacoes]


@router.post("/{fatura_id}/pagamentos", response_model=FaturaPagamentoResponse)
def pagar_fatura(
    fatura_id: int,
    pagamento_data: FaturaPagamentoCreate,
    db: Session = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_user),
) -> fatura.FaturaPagamento:
    """Registra um pagamento para a fatura"""
    # Verifica se a fatura existe e pertence ao usuário
    fatura = (
        db.query(Fatura)
        .filter(Fatura.id == fatura_id, Fatura.usuario_id == current_user.id)
        .first()
    )

    if not fatura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Fatura não encontrada"
        )

    if fatura.paga:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Fatura já está paga"
        )

    try:
        return FaturaService.processar_pagamento_fatura(
            db=db,
            fatura_id=fatura_id,
            valor=pagamento_data.valor_pago,
            forma_pagamento=pagamento_data.forma_pagamento,
            usuario_id=current_user.id,
            data_pagamento=pagamento_data.data_pagamento,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.get("/{fatura_id}/pagamentos", response_model=list[FaturaPagamentoResponse])
def listar_pagamentos_fatura(
    fatura_id: int,
    db: Session = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_user),
) -> list[fatura.FaturaPagamento]:
    """Lista os pagamentos de uma fatura"""
    fatura = (
        db.query(Fatura)
        .filter(Fatura.id == fatura_id, Fatura.usuario_id == current_user.id)
        .first()
    )

    if not fatura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Fatura não encontrada"
        )

    return fatura.pagamentos


@router.get("/resumo/{ano}/{mes}", response_model=FaturasResumoResponse)
def obter_resumo_faturas(
    ano: int,
    mes: int,
    db: Session = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict[str, float]:
    """Obtém resumo das faturas de um período"""
    return FaturaService.obter_resumo_faturas(
        db=db, usuario_id=current_user.id, ano=ano, mes=mes
    )


@router.get("/vencidas/alertas", response_model=FaturasVencidasAlertaResponse)
def obter_faturas_vencidas(
    db: Session = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_user),
) -> FaturasVencidasAlertaResponse:
    """Obtém todas as faturas vencidas do usuário"""
    faturas_vencidas = FaturaService.obter_faturas_vencidas(
        db=db, usuario_id=current_user.id
    )

    return FaturasVencidasAlertaResponse(
        total_vencidas=len(faturas_vencidas),
        valor_total_vencido=sum(f.saldo_devedor for f in faturas_vencidas),
        faturas=[FaturaResponse.model_validate(f) for f in faturas_vencidas],
    )
