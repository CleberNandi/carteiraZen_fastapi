from datetime import date, datetime
import enum

from app.schemas.base import BaseSchema


class TipoTransacaoEnum(str, enum.Enum):
    entrada = "entrada"
    saida = "saida"


class FormaPagamentoEnum(str, enum.Enum):
    pix = "pix"
    debito = "debito"
    dinheiro = "dinheiro"
    boleto = "boleto"
    cartao_credito = "cartao_credito"


class TransacaoBase(BaseSchema):
    descricao: str
    valor: float
    data: date
    tipo: TipoTransacaoEnum
    categoria_id: int
    conta_origem_id: int
    forma_pagamento: FormaPagamentoEnum
    fatura_id: int | None = None
    user_id: int | None = None


class TransacaoCreate(TransacaoBase):
    pass


class TransacaoUpdate(BaseSchema):
    descricao: str | None = None
    valor: float | None = None
    data: date | None = None
    tipo: TipoTransacaoEnum | None = None
    forma_pagamento: FormaPagamentoEnum
    categoria_id: int | None = None
    conta_origem_id: int | None = None
    fatura_id: int | None = None
    user_id: int | None = None


class TransacaoRead(TransacaoBase):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
