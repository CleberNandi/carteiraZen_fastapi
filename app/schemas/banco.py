from app.schemas.base import BaseSchema


class BancoBase(BaseSchema):
    nome: str
    codigo: str
    ispb: str | None = None
    cnpj: str | None = None
    site: str | None = None
    ativo: bool = True
    cor: str


class BancoCreate(BancoBase):
    pass


class BancoRead(BancoBase):
    id: int


class BancoReadWithContas(BancoRead):
    contas: list[int]
