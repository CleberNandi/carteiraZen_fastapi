from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import AuditMixin


class FaturaCartaoCredito(Base, AuditMixin):
    __tablename__ = "faturas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    cartao_id: Mapped[int] = mapped_column(ForeignKey("cartoes.id"))
    mes: Mapped[int] = mapped_column()
    ano: Mapped[int] = mapped_column()
    valor_total: Mapped[float] = mapped_column(default=0.0)
    status: Mapped[str] = mapped_column(default="aberta")  # aberta, fechada, paga
    ativo: Mapped[bool] = mapped_column(default=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    cartao = relationship("Cartao")
    transacoes = relationship("Transacao", back_populates="fatura")
    user = relationship("User")
