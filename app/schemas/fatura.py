from datetime import datetime
from enum import Enum

from app.schemas.base import BaseSchema


class StatusFaturaEnum(str, Enum):
    aberta = "aberta"
    fechada = "fechada"
    paga = "paga"


class FaturaBase(BaseSchema):
    cartao_id: int
    mes: int
    ano: int


class FaturaCreate(FaturaBase):
    valor_total: float | None = 0
    status: StatusFaturaEnum | None = StatusFaturaEnum.aberta
    ativo: bool | None = True


class FaturaUpdate(FaturaBase):
    valor_total: float | None = None
    status: StatusFaturaEnum | None = StatusFaturaEnum.aberta
    ativo: bool | None = True


class FaturaRead(FaturaBase):
    id: int
    valor_total: float
    status: str
    ativo: bool
    user_id: int
    created_at: datetime
