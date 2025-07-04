import enum
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class TipoTransacaoEnum(str, enum.Enum):
    despesa = "despesa"
    receita = "receita"


class TransacaoBase(BaseModel):
    descricao: str
    valor: float
    data: date
    tipo: TipoTransacaoEnum
    categoria_id: int
    conta_id: int
    fatura_id: int | None = None
    model_config = ConfigDict(from_attributes=True)


class TransacaoCreate(TransacaoBase):
    pass


class TransacaoUpdate(BaseModel):
    descricao: str | None = None
    valor: float | None = None
    data: date | None = None
    tipo: TipoTransacaoEnum | None = None
    categoria_id: int | None = None
    conta_id: int | None = None
    fatura_id: int | None = None
    model_config = ConfigDict(from_attributes=True)


class TransacaoRead(TransacaoBase):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)
