from datetime import date

from pydantic import Field

from app.schemas.base import BaseSchema


class FaturaBase(BaseSchema):
    data_fechamento: date
    data_vencimento: date
    data_inicio_periodo: date
    data_fim_periodo: date
    valor_total: int = Field(default=0, ge=0)
    valor_pago: int = Field(default=0, ge=0)
    valor_minimo: int = Field(default=0, ge=0)
    paga: bool = False
    vencida: bool = False
    juros_mora: int | None = None
    multa: int | None = None
    observacoes: str | None = None


class FaturaCreate(FaturaBase):
    cartao_id: int


class FaturaUpdate(BaseSchema):
    observacoes: str | None = None


class FaturaResponse(FaturaBase):
    id: int
    cartao_id: int
    usuario_id: int
    saldo_devedor: int
    percentual_pago: float
    dias_vencimento: int
    created_at: date | None = None
    updated_at: date | None = None

    class Config:
        from_attributes = True


class FaturaPagamentoCreate(BaseSchema):
    fatura_id: int
    valor_pago: int = Field(gt=0)
    forma_pagamento: str = Field(max_length=50)
    data_pagamento: date | None = None
    comprovante: str | None = None
    observacoes: str | None = None


class FaturaPagamentoResponse(BaseSchema):
    id: int
    fatura_id: int
    usuario_id: int
    valor_pago: int
    data_pagamento: date
    forma_pagamento: str
    comprovante: str | None = None
    observacoes: str | None = None
    created_at: date | None = None

    class Config:
        from_attributes = True


class FaturasResumoResponse(BaseSchema):
    total_faturas: int
    faturas_pagas: int
    faturas_vencidas: int
    faturas_pendentes: int
    valor_total: int
    valor_pago: int
    saldo_devedor: int
    percentual_quitado: float


class FaturasVencidasAlertaResponse(BaseSchema):
    total_vencidas: int
    valor_total_vencido: int
    faturas: list[FaturaResponse]
