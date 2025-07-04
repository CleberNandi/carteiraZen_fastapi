from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FaturaBase(BaseModel):
    cartao_id: int
    mes: int
    ano: int


class FaturaCreate(FaturaBase):
    ...


class FaturaUpdate(BaseModel):
    cartao_id: int | None = None
    mes: int | None = None
    ano: int | None = None
    valor_total: float | None = None
    status: str | None = None
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
