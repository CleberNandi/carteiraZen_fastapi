# app/schemas/transacao.py
from datetime import date

from pydantic import Field

from app.schemas.base import BaseSchema


# Schema base compartilhado
class TransacaoBase(BaseSchema):
    tipo: str = Field(..., max_length=20)
    valor_cents: int
    data_vencimento: date
    data_lancamento: date
    data_efetivacao: date
    encargos_cents: int | None = 0
    descontos_cents: int | None = 0
    recorrente: bool | None = False
    descricao: str | None = None
    efetivada: bool | None = True
    cor: str = Field(..., max_length=7)
    transacao_pai_id: int | None = None
    conta_origem_id: int | None = None
    conta_destino_id: int | None = None
    categoria_id: int | None = None
    sub_categoria_id: int | None = None
    fatura_id: int | None = None
    usuario_id: int


# Schema usado para criação
class TransacaoCreate(TransacaoBase):
    pass  # Herdamos todos os campos necessários


# Schema usado para leitura
class TransacaoRead(TransacaoBase):
    id: int
    created_at: str | None
    updated_at: str | None
    deleted_at: str | None
    ativo: bool
