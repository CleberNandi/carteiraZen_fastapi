from datetime import date

from app.schemas.base import BaseSchema


class FaturaBase(BaseSchema):
    valor_cents: int
    pago: bool = False
    cor: str
    fechamento: date
    vencimento: date
    ativo: bool = True
    conta_cartao_id: int
    usuario_id: int


class FaturaCreate(FaturaBase):
    pass


class FaturaRead(FaturaBase):
    id: int
