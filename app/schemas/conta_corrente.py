from enum import Enum

from app.schemas.base import BaseSchema


class TipoContaEnum(str, Enum):
    corrente = "corrente"
    poupanca = "poupanca"


class ContaBase(BaseSchema):
    numero: str
    digito: str
    nome: str
    agencia_id: int
    user_id: int
    saldo_inicial: float = 0.0
    tipo: TipoContaEnum = TipoContaEnum.corrente
    ativo: bool = True


class ContaCreate(ContaBase):
    pass


class ContaUpdate(ContaBase):
    pass


class ContaOut(ContaBase):
    id: int
