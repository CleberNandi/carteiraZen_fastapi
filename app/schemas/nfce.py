# app/schemas/nfce.py

from typing import ClassVar

from pydantic import Field

from app.schemas.base import BaseSchema


class ItemNFCE(BaseSchema):
    descricao: str
    quantidade: float
    valor_unitario: float
    valor_total: float
    unidade: str


class NFCEData(BaseSchema):
    cnpj_emitente: str = Field(..., alias="cnpj")
    emitente: str
    endereco: str
    valor_total: float
    numero: str
    serie: str
    data_emissao: str
    protocolo: str
    chave_acesso: str
    consumidor: str
    tributos: float
    itens: list[ItemNFCE]

    model_config: ClassVar[dict[str, bool | str]] = {
        "populate_by_name": True,
        "extra": "forbid",  # ou 'ignore' se quiser permitir extras sem erro
    }


class NFCERequest(BaseSchema):
    html: str
