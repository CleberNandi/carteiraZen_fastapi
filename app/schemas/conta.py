from app.schemas.base import BaseSchema


class ContaBase(BaseSchema):
    nome: str
    tipo: str
    saldo_cents: int = 0
    cheque_especial_cents: int = 0
    cor: str
    incluir_na_soma_inicial: bool = True
    conta_padrao: bool = False
    ativo: bool = True
    usuario_id: int
    banco_id: int | None = None


class ContaCreate(ContaBase):
    pass


class ContaRead(ContaBase):
    id: int
