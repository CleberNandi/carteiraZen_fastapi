# app/schemas/transacao.py
from datetime import date, datetime
from decimal import Decimal

from pydantic import Field, computed_field

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
    pass


# Schema usado para leitura (transação simples)
class TransacaoRead(TransacaoBase):
    id: int
    created_at: datetime | None
    updated_at: datetime | None
    deleted_at: datetime | None
    ativo: bool

    @computed_field
    @property
    def valor_decimal(self) -> float:
        return float(Decimal(self.valor_cents) / 100)


# === NOVOS SCHEMAS PARA TRANSAÇÕES PARCELADAS ===


class ParcelaResumo(BaseSchema):
    """Schema para resumo de parcela"""

    numero: int
    valor: float
    vencimento: date
    fatura_id: int


class TransacaoParceladaResumo(BaseSchema):
    """Schema para resumo da operação parcelada"""

    valor_total: float
    total_parcelas: int
    parcela_inicial: int
    parcelas_criadas: int


class TransacaoParceladaResponse(BaseSchema):
    """Schema de resposta para transações parceladas"""

    transacao: TransacaoRead
    parcelas: list[ParcelaResumo]
    resumo: TransacaoParceladaResumo


# === SCHEMAS PARA REQUISIÇÕES ===


class DespesaCartaoRequest(BaseSchema):
    """Schema para criação de despesa no cartão"""

    valor_cents: int = Field(..., gt=0, description="Valor em centavos")
    cartao_id: int
    categoria_id: int
    descricao: str = Field(..., min_length=1, max_length=255)
    data_transacao: date | None = None
    parcelas: int = Field(default=1, ge=1, le=48)
    parcela_inicial: int = Field(default=1, ge=1)


class ReceitaRequest(BaseSchema):
    """Schema para criação de receita"""

    valor_cents: int = Field(..., gt=0, description="Valor em centavos")
    conta_id: int
    categoria_id: int
    descricao: str = Field(..., min_length=1, max_length=255)
    data_transacao: date | None = None


class DespesaContaRequest(BaseSchema):
    """Schema para criação de despesa em conta"""

    valor_cents: int = Field(..., gt=0, description="Valor em centavos")
    conta_id: int
    categoria_id: int
    descricao: str = Field(..., min_length=1, max_length=255)
    meio_pagamento: str = Field(
        default="DEBITO", pattern="^(DEBITO|PIX|DINHEIRO|CREDITO)$"
    )
    data_transacao: date | None = None


class TransferenciaRequest(BaseSchema):
    """Schema para transferência entre contas"""

    valor_cents: int = Field(..., gt=0, description="Valor em centavos")
    conta_origem_id: int
    conta_destino_id: int
    descricao: str = Field(..., min_length=1, max_length=255)
    data_transacao: date | None = None


class TransferenciaResponse(BaseSchema):
    """Schema de resposta para transferências"""

    debito: TransacaoRead
    credito: TransacaoRead


# Schema original para compatibilidade
class TransacaoResponse(BaseSchema):
    id: int
    fatura_id: int
    valor: int
    descricao: str
    data: date
