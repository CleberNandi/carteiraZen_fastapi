from app.schemas.base import BaseSchema


class ItemNotaFiscalBase(BaseSchema):
    descricao: str
    quantidade: float
    unidade: str | None = None
    valor_unitario: float
    valor_total: float


class ItemNotaFiscalCreate(ItemNotaFiscalBase):
    pass


class ItemNotaFiscalRead(ItemNotaFiscalBase):
    id: int
