from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import ConfigDict, Field, computed_field, field_validator

from app.schemas.base import BaseSchema


class TipoConta(str, Enum):
    """Enum para tipos de conta"""

    CORRENTE = "CORRENTE"
    POUPANCA = "POUPANCA"
    INVESTIMENTO = "INVESTIMENTO"
    CARTEIRA = "CARTEIRA"
    OUTRO = "OUTRO"


class ContaBase(BaseSchema):
    nome: str = Field(..., min_length=1, max_length=100, description="Nome da conta")
    tipo: TipoConta = Field(..., description="Tipo da conta")
    saldo_cents: int = Field(default=0, description="Saldo em centavos")
    cheque_especial_cents: int = Field(
        default=0, ge=0, description="Limite do cheque especial em centavos"
    )
    cor: str = Field(
        ..., pattern=r"^#[0-9A-Fa-f]{6}$", description="Cor em formato hexadecimal"
    )
    incluir_na_soma_inicial: bool = Field(
        default=True, description="Incluir no saldo total inicial"
    )
    conta_padrao: bool = Field(
        default=False, description="Conta padrão para transações"
    )
    banco_id: int | None = Field(default=None, description="ID do banco")

    @field_validator("nome")
    @classmethod
    def validate_nome(cls, v: str) -> str:
        """Valida o nome da conta"""
        if not v.strip():
            message = "Nome da conta não pode estar vazio"
            raise ValueError(message)
        return v.strip().title()

    @field_validator("saldo_cents")
    @classmethod
    def validate_saldo(cls, v: int) -> int:
        """Valida o saldo (permite negativos para descoberto)"""
        if v < -100_000_000:  # -1 milhão de reais
            msg_saldo_menor = "Saldo não pode ser menor que -R$ 1.000.000,00"
            raise ValueError(msg_saldo_menor)
        if v > 1_000_000_000:  # 10 milhões de reais
            msg_saldo_maior = "Saldo não pode ser maior que R$ 10.000.000,00"
            raise ValueError(msg_saldo_maior)
        return v


class ContaCreate(ContaBase):
    """Schema para criação de conta"""

    usuario_id: int | None = Field(
        default=None, description="ID do usuário (preenchido automaticamente)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nome": "Conta Corrente Banco do Brasil",
                "tipo": "CORRENTE",
                "saldo_cents": 150000,  # R$ 1.500,00
                "cheque_especial_cents": 100000,  # R$ 1.000,00
                "cor": "#1E88E5",
                "incluir_na_soma_inicial": True,
                "conta_padrao": False,
                "banco_id": 1,
            }
        }
    )


class ContaUpdate(BaseSchema):
    """Schema para atualização de conta"""

    nome: str | None = Field(None, min_length=1, max_length=100)
    cheque_especial_cents: int | None = Field(None, ge=0)
    cor: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    incluir_na_soma_inicial: bool | None = None
    conta_padrao: bool | None = None

    @field_validator("nome")
    @classmethod
    def validate_nome(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            message = "Nome da conta não pode estar vazio"
            raise ValueError(message)
        return v.strip().title() if v else v


class ContaRead(ContaBase):
    """Schema para leitura de conta"""

    id: int
    usuario_id: int
    created_at: datetime | None
    updated_at: datetime | None
    deleted_at: datetime | None
    ativo: bool

    @computed_field
    @property
    def saldo_decimal(self) -> float:
        """Retorna o saldo em formato decimal"""
        return float(Decimal(self.saldo_cents) / 100)

    @computed_field
    @property
    def cheque_especial_decimal(self) -> float:
        """Retorna o limite do cheque especial em formato decimal"""
        return float(Decimal(self.cheque_especial_cents) / 100)

    @computed_field
    @property
    def saldo_disponivel_decimal(self) -> float:
        """Retorna o saldo disponível (saldo + cheque especial) em formato decimal"""
        return float(Decimal(self.saldo_cents + self.cheque_especial_cents) / 100)

    @computed_field
    @property
    def status_saldo(self) -> str:
        """Retorna o status do saldo"""
        if self.saldo_cents > 0:
            return "POSITIVO"
        if self.saldo_cents == 0:
            return "ZERO"
        if self.saldo_cents > -self.cheque_especial_cents:
            return "CHEQUE_ESPECIAL"
        return "NEGATIVO"


class ContaResumo(BaseSchema):
    """Schema para resumo de conta (listagens)"""

    id: int
    nome: str
    tipo: TipoConta
    saldo_decimal: float
    cor: str
    ativo: bool
    conta_padrao: bool


class ContaListResponse(BaseSchema):
    """Schema para resposta de listagem"""

    contas: list[ContaResumo]
    total: int
    saldo_total: float
