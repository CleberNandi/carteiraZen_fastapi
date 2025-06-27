from pydantic import BaseModel, ConfigDict


class BancoBase(BaseModel):
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
    model_config = ConfigDict(from_attributes=True)
