from app.schemas.base import BaseSchema


class BancoBase(BaseSchema):
    nome: str
    codigo: str
    ispb: str | None = None
    cnpj: str | None = None
    site: str | None = None
    ativo: bool | None = True


class BancoCreate(BancoBase):
    pass


class Banco(BancoBase):
    id: int
