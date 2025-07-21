from enum import Enum

from pydantic import BaseModel, ConfigDict


class TipoContaEnum(str, Enum):
    corrente = "corrente"
    poupanca = "poupanca"


class ContaBase(BaseModel):
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
    model_config = ConfigDict(from_attributes=True)
