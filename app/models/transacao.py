from datetime import UTC, datetime
import enum

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import AuditMixin


class FormaPagamentoEnum(str, enum.Enum):
    pix = "pix"
    debito = "debito"
    dinheiro = "dinheiro"
    boleto = "boleto"
    cartao_credito = "cartao_credito"


class TipoTransacaoEnum(str, enum.Enum):
    entrada = "entrada"
    saida = "saida"


class Transacao(Base, AuditMixin):
    __tablename__ = "transacoes"

    descricao: Mapped[str] = mapped_column(String(255))
    valor: Mapped[float] = mapped_column()
    data: Mapped[datetime] = mapped_column(default=datetime.now(UTC))
    tipo: Mapped[TipoTransacaoEnum] = mapped_column(Enum(TipoTransacaoEnum))
    forma_pagamento: Mapped[FormaPagamentoEnum] = mapped_column(
        Enum(FormaPagamentoEnum)
    )
    conta_origem_id: Mapped[int] = mapped_column(ForeignKey("contas.id"))
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"))
    fatura_id: Mapped[int | None] = mapped_column(
        ForeignKey("faturas.id"), nullable=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    conta_origem = relationship("Conta")
    categoria = relationship("Categoria")
    fatura = relationship("Fatura", back_populates="transacoes")
    user = relationship("User")
