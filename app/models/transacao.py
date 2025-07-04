import enum
from datetime import UTC, datetime

from sqlalchemy import Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class FormaPagamentoEnum(str, enum.Enum):
    pix = "pix"
    debito = "debito"
    dinheiro = "dinheiro"
    boleto = "boleto"
    cartao_credito = "cartao_credito"


class TipoTransacaoEnum(str, enum.Enum):
    entrada = "entrada"
    saida = "saida"


class Transacao(Base):
    __tablename__ = "transacoes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    descricao: Mapped[str] = mapped_column(String(255))
    valor: Mapped[float] = mapped_column()
    data: Mapped[datetime] = mapped_column(default=datetime.now(UTC))
    tipo: Mapped[TipoTransacaoEnum] = mapped_column(Enum(TipoTransacaoEnum))
    forma_pagamento: Mapped[FormaPagamentoEnum] = mapped_column(
        Enum(FormaPagamentoEnum)
    )
    conta_origem_id: Mapped[int] = mapped_column(ForeignKey("contas_correntes.id"))
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"))
    fatura_id: Mapped[int | None] = mapped_column(
        ForeignKey("faturas.id"), nullable=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    ativo: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    created_by: Mapped[int] = mapped_column(nullable=True)
    updated_at: Mapped[datetime] = mapped_column(onupdate=func.now())
    updated_by: Mapped[int] = mapped_column(nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(nullable=True)
    deleted_by: Mapped[int] = mapped_column(nullable=True)

    conta_origem = relationship("ContaCorrente")
    categoria = relationship("Categoria")
    fatura = relationship("FaturaCartaoCredito", back_populates="transacoes")
    user = relationship("User")
