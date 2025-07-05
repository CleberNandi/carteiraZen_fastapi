import enum
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class TipoTransacaoEnum(str, enum.Enum):
    despesa = "despesa"
    receita = "receita"


class FormaPagamentoEnum(str, enum.Enum):
    pix = "pix"
    debito = "debito"
    dinheiro = "dinheiro"
    boleto = "boleto"
    cartao_credito = "cartao_credito"


class TransacaoBase(BaseModel):
    descricao: str
    valor: float
    data: date
    tipo: TipoTransacaoEnum
    categoria_id: int
    conta_origem_id: int
    forma_pagamento: FormaPagamentoEnum
    fatura_id: int | None = None
    user_id: int | None = None
    model_config = ConfigDict(from_attributes=True)


class TransacaoCreate(TransacaoBase):
    pass


class TransacaoUpdate(BaseModel):
    descricao: str | None = None
    valor: float | None = None
    data: date | None = None
    tipo: TipoTransacaoEnum | None = None
    categoria_id: int | None = None
    conta_origem_id: int | None = None
    fatura_id: int | None = None
    model_config = ConfigDict(from_attributes=True)


class TransacaoRead(TransacaoBase):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)
