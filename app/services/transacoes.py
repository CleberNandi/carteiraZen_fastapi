# app/services/transacoes.py

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.crud.conta_corrente import get_conta_corrente
from app.crud.fatura import get_fatura
from app.crud.transacao import create_transacao
from app.schemas.transacao import FormaPagamentoEnum, TipoTransacaoEnum, TransacaoCreate


def criar_transacao(
    db: Session, transacao: TransacaoCreate, user_id: int
) -> TransacaoCreate:
    if transacao.forma_pagamento == FormaPagamentoEnum.cartao_credito:
        # Valida existência de fatura
        if not transacao.fatura_id:
            raise HTTPException(
                status_code=400, detail="Fatura é obrigatória para cartão de crédito."
            )

        fatura = get_fatura(db, transacao.fatura_id)

        if not fatura:
            raise HTTPException(
                status_code=404, detail="Fatura não encontrada ou inativa."
            )

        # Atualiza valor da fatura
        fatura.valor_total += transacao.valor
        db.add(fatura)
        db.commit()
        db.refresh(fatura)

    else:
        # Para qualquer outro tipo de pagamento, atualizar saldo da conta
        conta = get_conta_corrente(db, transacao.conta_origem_id)

        if not conta:
            raise HTTPException(
                status_code=404, detail="Conta de origem não encontrada."
            )

        if transacao.tipo == TipoTransacaoEnum.saida:
            conta.saldo_inicial -= transacao.valor
        else:
            conta.saldo_inicial += transacao.valor

        db.add(conta)
        db.commit()
        db.refresh(conta)

    # Cria a transação em si
    return create_transacao(db=db, transacao=transacao, user_id=user_id)
