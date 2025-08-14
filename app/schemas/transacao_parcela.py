from app.schemas.base import BaseSchema


class TransacaoParcelaBase(BaseSchema):
    quantidade: int | None = None
    parcela_inicial: int | None = None
    periodicidade: str = "mensal"
    ativo: bool = True
    transacao_id: int | None = None
    usuario_id: int


class TransacaoParcelaCreate(TransacaoParcelaBase):
    pass


class TransacaoParcelaRead(TransacaoParcelaBase):
    id: int
