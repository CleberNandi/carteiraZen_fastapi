# app/services/faturas.py

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models
from app.crud.fatura import create_fatura, get_fatura_existente
from app.schemas.fatura import FaturaCreate, StatusFaturaEnum


def criar_fatura(db: Session, fatura: FaturaCreate, user_id: int) -> models.Fatura:
    # 1. Verifica se já existe uma fatura com mesmo cartao_id, mes, ano
    fatura_existente = get_fatura_existente(
        db, cartao_id=fatura.cartao_id, mes=fatura.mes, ano=fatura.ano
    )
    if fatura_existente:
        raise HTTPException(
            status_code=400, detail="Fatura já existe para esse mês e cartão."
        )

    # 2. Garante valor inicial e status padrão
    fatura_completa = fatura.model_copy()
    fatura_completa.valor_total = 0.0
    fatura_completa.status = StatusFaturaEnum.aberta
    fatura_completa.ativo = True

    # 3. Cria e retorna via CRUD
    return create_fatura(db, fatura_completa, user_id)
