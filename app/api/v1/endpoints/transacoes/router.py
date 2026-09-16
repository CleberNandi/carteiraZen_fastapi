from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.dependencies import get_current_user
from app.models import usuario
from app.schemas.transacao import (
    DespesaCartaoRequest,
    DespesaContaRequest,
    ReceitaRequest,
    TransacaoParceladaResponse,
    TransacaoRead,
    TransferenciaRequest,
    TransferenciaResponse,
)
from app.services.transacao_service import TransacaoService

router = APIRouter()

Usuario = usuario.Usuario


@router.post("/cartao/despesa", response_model=TransacaoParceladaResponse)
async def criar_despesa_cartao(
    request: DespesaCartaoRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_user),
) -> TransacaoRead:
    """Cria despesa no cartão com parcelas"""

    return await TransacaoService.criar_despesa_cartao(
        db=db,
        valor_cents=request.valor_cents,
        cartao_id=request.cartao_id,
        categoria_id=request.categoria_id,
        descricao=request.descricao,
        usuario_id=current_user.id,
        data_transacao=request.data_transacao,
        parcelas=request.parcelas,
        parcela_inicial=request.parcela_inicial,
    )


@router.post("/receita", response_model=TransacaoRead)
async def criar_receita(
    request: ReceitaRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_user),
) -> TransacaoRead:
    """Cria receita na conta"""

    return await TransacaoService.criar_receita(
        db=db,
        valor_cents=request.valor_cents,
        conta_id=request.conta_id,
        categoria_id=request.categoria_id,
        descricao=request.descricao,
        usuario_id=current_user.id,
        data_transacao=request.data_transacao,
    )


@router.post("/despesa/conta", response_model=TransacaoRead)
async def criar_despesa_conta(
    request: DespesaContaRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_user),
) -> TransacaoRead:
    """Cria despesa diretamente na conta"""

    return await TransacaoService.criar_despesa_conta(
        db=db,
        valor_cents=request.valor_cents,
        conta_id=request.conta_id,
        categoria_id=request.categoria_id,
        descricao=request.descricao,
        usuario_id=current_user.id,
        meio_pagamento=request.meio_pagamento,
        data_transacao=request.data_transacao,
    )


@router.post("/transferencia", response_model=TransferenciaResponse)
async def transferir_entre_contas(
    request: TransferenciaRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict[str, TransacaoRead]:
    """Transfere dinheiro entre contas"""

    return await TransacaoService.transferir_entre_contas(
        db=db,
        valor_cents=request.valor_cents,
        conta_origem_id=request.conta_origem_id,
        conta_destino_id=request.conta_destino_id,
        descricao=request.descricao,
        usuario_id=current_user.id,
        data_transacao=request.data_transacao,
    )
