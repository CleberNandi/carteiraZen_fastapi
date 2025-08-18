from datetime import date

from pydantic import Field

from app.schemas.base import BaseSchema


class OrcamentoBase(BaseSchema):
    categoria_id: int
    ano: int = Field(ge=2020, le=2030)
    mes: int = Field(ge=1, le=12)
    valor_limite: int = Field(gt=0)
    notificar_em: int = Field(default=80, ge=50, le=100)


class OrcamentoCreate(OrcamentoBase):
    pass


class OrcamentoUpdate(BaseSchema):
    valor_limite: int | None = Field(None, gt=0)
    notificar_em: int | None = Field(None, ge=50, le=100)
    ativo: bool | None = None


class OrcamentoResponse(OrcamentoBase):
    id: int
    usuario_id: int
    valor_gasto: int
    valor_disponivel: int
    percentual_usado: float
    excedeu_limite: bool
    deve_notificar: bool
    ativo: bool
    created_at: date | None = None
    updated_at: date | None = None

    # Dados da categoria
    categoria: dict[str, str]


class ResumoOrcamentosResponse(BaseSchema):
    total_orcamentos: int
    total_orcado: int
    total_gasto: int
    total_disponivel: int
    percentual_usado: float
    orcamentos_excedidos: int
    orcamentos_alerta: int
    orcamentos_ok: int


class OrcamentosExcedidosResponse(BaseSchema):
    total_excedidos: int
    valor_total_excesso: float
    orcamentos: list[OrcamentoResponse]


class OrcamentosAlertaResponse(BaseSchema):
    total_alertas: int
    orcamentos: list[OrcamentoResponse]


class ComparativoOrcamentoResponse(BaseSchema):
    categoria: str
    cor: str
    valor_orcado: float
    valor_gasto: float
    valor_disponivel: float
    percentual_usado: float
    excedeu: bool
    status: str
