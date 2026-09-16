from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from mixins.sync_mixins import SyncMixin
from sqlalchemy import BigInteger, Boolean, Date, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.mixins.mixins import Mixins

if TYPE_CHECKING:
    from models.fatura import Fatura, FaturaPagamento
    from models.transacao import Transacao
    from models.usuario import Usuario


class TransacaoParcela(Base, Mixins, SyncMixin):
    __tablename__ = "transacoes_parcelas"

    # Identificação da parcela
    numero_parcela: Mapped[int] = mapped_column(Integer, nullable=False)  # 1, 2, 3...
    total_parcelas: Mapped[int] = mapped_column(Integer, nullable=False)  # 12x total

    # Valores (em centavos para precisão)
    valor_cents: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # Datas
    data_vencimento: Mapped[Date] = mapped_column(Date, nullable=False)

    # Status da parcela
    paga: Mapped[bool] = mapped_column(Boolean, default=False)
    cancelada: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relacionamentos
    transacao_id: Mapped[int] = mapped_column(
        ForeignKey("transacoes.id"), nullable=False
    )
    fatura_id: Mapped[int | None] = mapped_column(ForeignKey("faturas.id"))
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)

    transacao: Mapped["Transacao"] = relationship(back_populates="parcelas")  # type: ignore[name-defined]
    fatura: Mapped["Fatura"] = relationship(back_populates="parcelas")  # type: ignore[name-defined]
    usuario: Mapped["Usuario"] = relationship(back_populates="transacoes_parcelas")  # type: ignore[name-defined]
    fatura_pagamento_id: Mapped[int | None] = mapped_column(
        ForeignKey("faturas_pagamentos.id")
    )
    fatura_pagamento: Mapped[Optional["FaturaPagamento"]] = relationship(
        back_populates="parcelas"
    )

    @property
    def valor_decimal(self) -> Decimal:
        """Retorna valor em decimal"""
        return Decimal(self.valor_cents) / 100

    @property
    def descricao_parcela(self) -> str:
        """Retorna descrição formatada da parcela"""
        return f"Parcela {self.numero_parcela}/{self.total_parcelas}"

    def __repr__(self) -> str:
        return f"<Parcela {self.numero_parcela}/{self.total_parcelas} - R${self.valor_decimal}>"
