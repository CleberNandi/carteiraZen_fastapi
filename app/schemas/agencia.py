from app.schemas.base import BaseSchema


class AgenciaBase(BaseSchema):
    numero: str
    digito: str | None = None
    banco_id: int
    nome: str | None = None
    ativo: bool | None = True


class AgenciaCreate(AgenciaBase):
    pass


class Agencia(AgenciaBase):
    id: int
