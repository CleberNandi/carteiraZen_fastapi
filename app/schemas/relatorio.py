# schemas/dashboard.py
from decimal import Decimal
from typing import Any

from app.schemas.base import BaseSchema


class Periodo(BaseSchema):
    ano: int
    mes: int


class Resumo(BaseSchema):
    total_gasto_mes: Decimal
    faturas_pendentes: int
    valor_faturas_pendentes: Decimal
    orcamentos_excedidos: int
    total_orcado: Decimal
    percentual_orcamento_usado: float


class GastoCategoria(BaseSchema):
    categoria: str
    cor: str
    valor: Decimal
    percentual: float


class GastoMensalResponse(BaseSchema):
    mes: int
    nome: str
    valor: float


class RelatorioResponse(BaseSchema):
    periodo: Periodo
    resumo: Resumo
    gastos_por_categoria: list[GastoCategoria]
    ultimas_transacoes: list[dict[str, Any]]
