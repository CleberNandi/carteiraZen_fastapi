from datetime import datetime

from app.schemas.base import BaseSchema


class AuditoriaBase(BaseSchema):
    tabela: str
    registro_id: int
    acao: str
    user_id: int | None = None
    data: datetime | None = None
    dados_antes: str | None = None
    dados_input: str | None = None
    dados_depois: str | None = None


class Auditoria(AuditoriaBase):
    id: int


class AuditoriaFiltro(BaseSchema):
    tabela: str | None = None
    registro_id: int | None = None
    acao: str | None = None
    user_id: int | None = None
    skip: int = 0
    limit: int = 100
