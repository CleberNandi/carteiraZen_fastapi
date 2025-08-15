from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import Field

from app.schemas.base import BaseSchema

if TYPE_CHECKING:
    from datetime import datetime

    from app.schemas.nfce_itens import ItemNotaFiscalCreate, ItemNotaFiscalRead


class NotaFiscalBase(BaseSchema):
    emitente: str
    cnpj: str
    endereco: str | None = None
    valor_total: float
    numero: str
    serie: str | None = None
    data_emissao: datetime
    protocolo: str | None = None
    chave_acesso: str
    consumidor: str | None = None
    tributos: float | None = None


class NotaFiscalCreate(NotaFiscalBase):
    itens: list[ItemNotaFiscalCreate] = Field(default_factory=list)  # type: ignore


class NotaFiscalRead(NotaFiscalBase):
    id: int
    itens: list[ItemNotaFiscalRead] = Field(default_factory=list)  # type: ignore
