from enum import Enum

from app.schemas.base import BaseSchema


class TipoContaEnum(str, Enum):
    corrente = "corrente"
    poupanca = "poupanca"


class ContaBase(BaseSchema):
    nome: str
    numero: str
    agencia: str | None = None
    user_id: int
    saldo_inicial: float = 0.0
    tipo: TipoContaEnum = TipoContaEnum.corrente
    ativo: bool = True


class ContaCreate(ContaBase):
    pass


class ContaUpdate(BaseSchema):
    nome: str
    numero: str
    user_id: int
    saldo_inicial: float = 0.0
    tipo: TipoContaEnum = TipoContaEnum.corrente
    ativo: bool = True


class ContaOut(ContaBase):
    id: int
