from datetime import datetime

from pydantic import BaseModel


class AuditoriaBase(BaseModel):
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


class AuditoriaFiltro(BaseModel):
    tabela: str | None = None
    registro_id: int | None = None
    acao: str | None = None
    user_id: int | None = None
    skip: int = 0
    limit: int = 100
