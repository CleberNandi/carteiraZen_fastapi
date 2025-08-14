from datetime import date

from app.schemas.base import BaseSchema


class CartaoBase(BaseSchema):
    numero: str
    descricao: str
    bandeira: str
    limite_cents: int
    fechamento: date
    vencimento: date
    cartao_padrao: bool = False
    cor: str
    ativo: bool = True
    conta_id: int
    usuario_id: int


class CartaoCreate(CartaoBase):
    pass


class CartaoRead(CartaoBase):
    id: int
