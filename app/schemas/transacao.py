# app/schemas/transacao.py
from datetime import date
from typing import Optional

from pydantic import Field

from app.schemas.base import BaseSchema


# Schema base compartilhado
class TransacaoBase(BaseSchema):
    tipo: str = Field(..., max_length=20)
    valor_cents: int
    data_vencimento: date
    data_lancamento: date
    data_efetivacao: date
    encargos_cents: Optional[int] = 0
    descontos_cents: Optional[int] = 0
    recorrente: Optional[bool] = False
    descricao: Optional[str] = None
    efetivada: Optional[bool] = True
    cor: str = Field(..., max_length=7)
    transacao_pai_id: Optional[int] = None
    conta_origem_id: Optional[int] = None
    conta_destino_id: Optional[int] = None
    categoria_id: Optional[int] = None
    sub_categoria_id: Optional[int] = None
    fatura_id: Optional[int] = None
    usuario_id: int


# Schema usado para criação
class TransacaoCreate(TransacaoBase):
    pass  # Herdamos todos os campos necessários


# Schema usado para leitura
class TransacaoRead(TransacaoBase):
    id: int
    created_at: Optional[str]
    updated_at: Optional[str]
    deleted_at: Optional[str]
    ativo: bool
