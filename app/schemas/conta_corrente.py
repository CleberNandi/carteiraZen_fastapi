from enum import Enum

from pydantic import BaseModel, ConfigDict


class TipoContaEnum(str, Enum):
    corrente = "corrente"
    poupanca = "poupanca"


class ContaCorrenteBase(BaseModel):
    numero: str
    digito: str | None = None
    agencia_id: int
    user_id: int
    saldo_inicial: float = 0.0
    tipo: TipoContaEnum = TipoContaEnum.corrente
    ativo: bool | None = True


class ContaCorrenteCreate(ContaCorrenteBase):
    pass


class ContaCorrente(ContaCorrenteBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
