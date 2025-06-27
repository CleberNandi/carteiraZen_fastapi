from pydantic import BaseModel, ConfigDict


class AgenciaBase(BaseModel):
    numero: str
    digito: str | None = None
    banco_id: int
    nome: str | None = None
    ativo: bool | None = True


class AgenciaCreate(AgenciaBase):
    pass


class Agencia(AgenciaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
