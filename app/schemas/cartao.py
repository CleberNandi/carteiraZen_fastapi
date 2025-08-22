from app.schemas.base import BaseSchema


class CartaoBase(BaseSchema):
    numero: str
    descricao: str
    bandeira: str
    limite_cents: int
    dia_fechamento: int
    dias_vencimento: int
    cartao_padrao: bool = False
    cor: str
    ativo: bool = True
    conta_id: int


class CartaoCreate(CartaoBase):
    pass


class CartaoRead(CartaoBase):
    id: int
