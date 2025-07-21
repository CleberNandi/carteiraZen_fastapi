from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class StatusFaturaEnum(str, Enum):
    aberta = "aberta"
    fechada = "fechada"
    paga = "paga"


class FaturaBase(BaseModel):
    cartao_id: int
    mes: int
    ano: int


class FaturaCreate(FaturaBase):
    valor_total: float | None = None
    status: StatusFaturaEnum | None = None
    ativo: bool | None = None


class FaturaUpdate(FaturaBase):
    valor_total: float | None = None
    status: StatusFaturaEnum | None = None
    ativo: bool | None = None

    model_config = ConfigDict(from_attributes=True)


class FaturaRead(FaturaBase):
    id: int
    valor_total: float
    status: str
    ativo: bool
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
